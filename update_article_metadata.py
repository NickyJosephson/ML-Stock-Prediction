import pymysql
import requests
from datetime import datetime, timedelta
import json
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Database connection configuration
DB_HOST = os.getenv("RDS_HOST")
DB_USER = os.getenv("RDS_USER")
DB_PASSWORD = os.getenv("RDS_PASSWORD")
DB_NAME = os.getenv("RDS_DATABASE")

# Headers for web requests
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
}

# Function to connect to the database
def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

# Function to fetch articles in chunks
def fetch_articles_from_db(connection, last_id, limit=1000):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id, url FROM articles WHERE article_content IS NULL AND id > %s ORDER BY id ASC LIMIT %s",
            (last_id, limit)
        )
        return cursor.fetchall()
    
def extract_article_content(html_content):
    """
    Extract the main article content from the given HTML content.
    Handles older articles with specific structures.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Strategy 1: Extract paragraphs with specific class
    paragraphs = soup.find_all("p", class_="col-body mb-4 text-lg md:leading-8 break-words min-w-0")
    if paragraphs:
        return " ".join(paragraph.get_text(strip=True) for paragraph in paragraphs)

    # Strategy 2: Extract all <p> tags as fallback
    generic_paragraphs = soup.find_all("p")
    if generic_paragraphs:
        return " ".join(paragraph.get_text(strip=True) for paragraph in generic_paragraphs)

    # Strategy 3: Default empty content
    return "No article content found."

# Function to parse an individual article
def parse_individual_article(html_content):
    """
    Parse an individual article and extract all relevant metadata.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    stock_symbols = []
    keywords = []
    date_published = None
    date_modified = None
    article_content = extract_article_content(html_content)  # Call updated function

    # Extract stock symbols
    ticker_links = soup.find_all("a", {"data-testid": "ticker-container"})
    for ticker in ticker_links:
        symbol_span = ticker.find("span", class_="symbol")
        if symbol_span:
            stock_symbols.append(symbol_span.text.strip())

    # Extract metadata from JSON-LD script
    script_tag = soup.find("script", type="application/ld+json")
    if script_tag:
        try:
            data = json.loads(script_tag.string)
            date_published = data.get("datePublished")
            date_modified = data.get("dateModified")
            keywords = data.get("keywords", [])
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

    return {
        "stock_symbols": stock_symbols,
        "keywords": keywords,
        "date_published": date_published,
        "date_modified": date_modified,
        "article_content": article_content,
    }

# Function to update the article in the database
def update_article_in_db(connection, article_id, data):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE articles
            SET stock_symbols = %s,
                keywords = %s,
                date_published = %s,
                date_modified = %s,
                article_content = %s
            WHERE id = %s
            """,
            (
                json.dumps(data["stock_symbols"]),
                json.dumps(data["keywords"]),
                data["date_published"],
                data["date_modified"],
                data["article_content"],
                article_id
            )
        )
        connection.commit()

# Main function
def main():
    connection = get_db_connection()
    batch_size = 1000
    last_id = 0

    while True:
        articles = fetch_articles_from_db(connection, last_id=last_id, limit=batch_size)
        if not articles:
            break

        for article in articles:
            article_id = article["id"]
            url = article["url"]
            try:
                print(f"Processing article ID: {article_id}, URL: {url}")
                response = requests.get(url, headers=HEADERS, timeout=10)
                if response.status_code == 200:
                    data = parse_individual_article(response.text)
                    update_article_in_db(connection, article_id, data)
                else:
                    print(f"Failed to fetch article {url}, Status Code: {response.status_code}")
            except Exception as e:
                print(f"Error processing article ID {article_id}: {e}")

        last_id = articles[-1]["id"]  # Update last_id to the highest processed ID

    connection.close()

if __name__ == "__main__":
    main()