import requests
import gzip
import io
import os
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta, timezone

# Directory to save downloaded sitemaps and the resulting CSV
SITEMAP_DIR = "sitemaps"
CSV_FILE = "financial_articles.csv"

# Headers to mimic a browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
}

# Ensure the directory for storing sitemaps exists
if not os.path.exists(SITEMAP_DIR):
    os.makedirs(SITEMAP_DIR)

# Function to fetch and decompress a sitemap file
def fetch_and_decompress_sitemap(url):
    print(f"Fetching sitemap: {url}")
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as f:
                xml_content = f.read().decode("utf-8")
            return xml_content
        else:
            print(f"Failed to fetch {url}: HTTP {response.status_code}")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None

# Function to parse the XML and extract article URLs
def parse_sitemap(xml_content):
    articles = []
    soup = BeautifulSoup(xml_content, "xml")
    for loc in soup.find_all("loc"):
        url = loc.text.strip()
        title = url.split("/")[-1].replace("-", " ").replace(".html", "")
        lastmod_tag = loc.find_next_sibling("lastmod")
        lastmod = lastmod_tag.text.strip() if lastmod_tag else None
        articles.append({"url": url, "title": title, "last_modified": lastmod})
    return articles

# Function to save articles to a CSV file
def save_to_csv(articles):
    new_df = pd.DataFrame(articles)
    if os.path.exists(CSV_FILE):
        existing_df = pd.read_csv(CSV_FILE)
        combined_df = pd.concat([existing_df, new_df]).drop_duplicates(subset=["url"])
    else:
        combined_df = new_df
    combined_df.to_csv(CSV_FILE, index=False)
    print(f"Saved {len(articles)} new articles to {CSV_FILE}.")

# Function to determine the starting date based on existing data
def get_start_date():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        if not df.empty:
            # Parse the "last_modified" column as datetime in UTC
            last_date = pd.to_datetime(df["last_modified"], utc=True).max()
            return last_date
    # Default to start from a predefined date if no file exists
    return datetime(2018, 10, 28, tzinfo=timezone.utc)


# Main function to fetch and process all sitemaps
def main():
    # Determine the start date
    start_date = get_start_date()
    end_date = datetime.now(timezone.utc)

    # Iterate through dates to construct sitemap URLs
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        sitemap_url = f"https://finance.yahoo.com/sitemaps/finance-sitemap_articles_{date_str}_US_en-US.xml.gz"
        
        # Fetch and decompress sitemap
        xml_content = fetch_and_decompress_sitemap(sitemap_url)
        if xml_content:
            # Parse and save articles
            articles = parse_sitemap(xml_content)
            if articles:
                save_to_csv(articles)

        # Move to the next day
        current_date += timedelta(days=1)

if __name__ == "__main__":
    main()