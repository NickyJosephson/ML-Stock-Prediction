import requests
import pymysql
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

# Base URL for Yahoo Finance sitemap
BASE_URL = "https://finance.yahoo.com/sitemap/"

# AWS RDS MySQL Configuration
# Headers to mimic a browser
HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "text/plain;charset=UTF-8",
    "origin": "https://finance.yahoo.com",
    "referer": "https://finance.yahoo.com",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
}

load_dotenv()

# Parse the HTML response and extract articles
def parse_articles(html_content, date_str):
    soup = BeautifulSoup(html_content, "html.parser")
    articles = []
    ul_tag = soup.find("ul", class_="Fz(14px) M(0) P(0)")
    if ul_tag:
        for li in ul_tag.find_all("li", class_="List(n) Py(3px) Lh(1.2)"):
            link = li.find("a")
            if link:
                title = link.text.strip()
                url = link["href"].strip()
                articles.append({"date_published": date_str, "title": title, "url": url})
    return articles

# Connect to RDS MySQL
def get_db_connection():
    return pymysql.connect(
        host=os.getenv("RDS_HOST"),
        port=int(os.getenv("RDS_PORT")),
        user=os.getenv("RDS_USER"),
        password=os.getenv("RDS_PASSWORD"),
        database=os.getenv("RDS_DATABASE"),
        cursorclass=pymysql.cursors.DictCursor,  # Use DictCursor here
    )

# Save articles to RDS MySQL
def save_to_rds(articles):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            for article in articles:
                sql = """
                INSERT INTO articles (date_published, title, url)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE title = VALUES(title), url = VALUES(url)
                """
                cursor.execute(sql, (article["date_published"], article["title"], article["url"]))
        connection.commit()
        print(f"Saved {len(articles)} articles to RDS.")
    finally:
        connection.close()

# Get the latest date from the database
def get_start_date():
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT MAX(date_published) as last_date FROM articles")
        result = cursor.fetchone()  # Fetch a single dictionary result
    connection.close()

    if result and result["last_date"]:  # Access the result using dictionary keys
        # Directly return the datetime.date object as a datetime
        return datetime.combine(result["last_date"], datetime.min.time())
    else:
        # Default to start from a predefined date if no data exists
        return datetime.strptime("2012-06-01", "%Y-%m-%d")

def calculate_start_time(date_str):
    date_obj = datetime.strptime(date_str, "%Y_%m_%d")
    date_obj = date_obj.replace(hour=9, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
    return int(date_obj.timestamp() * 1000)

# Fetch articles for all dates, handling pagination
def fetch_all_news(start_date):
    current_date = start_date
    end_date = datetime.now()
    while current_date <= end_date:
        # Format the date in the required format (YYYY_MM_DD)
        date_str = current_date.strftime("%Y_%m_%d")
        
        # Initialize pagination with the correct start time
        first = True
        start_time = calculate_start_time(date_str)
        while True:
            # Construct the URL with pagination
            url = f"{BASE_URL}{date_str}"
            if not first:
                url = f"{BASE_URL}{date_str}_start{start_time}"
            try:
                response = requests.get(url, headers=HEADERS)
                if response.status_code == 200:
                    print(f"Successfully fetched data for {date_str} (start={start_time})")
                    articles = parse_articles(response.text, date_str)
                    if not articles:  # Break if no articles are found on this page
                        break
                    save_to_rds(articles)
                else:
                    print(f"Failed to fetch data for {date_str} (start={start_time}), Status Code: {response.status_code}")
                    break
            except Exception as e:
                print(f"Error fetching data for {date_str} (start={start_time}): {e}")
                break

            # Increment _start by a fixed amount (e.g., 2 hours = 7200000 ms)
            if not first:
                start_time += 7200000
            first = False        
        # Move to the next day
        current_date += timedelta(days=1)

# Main function
if __name__ == "__main__":
    print("Fetching Yahoo Finance articles...")
    start_date = get_start_date() + timedelta(days=1)  # Start from the next day
    fetch_all_news(start_date)