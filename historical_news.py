import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup
import os

# Base URL for Yahoo Finance sitemap
BASE_URL = "https://finance.yahoo.com/sitemap/"

# File to save the data
CSV_FILE = "json_financial_news.csv"

# Headers to mimic a browser
HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "text/plain;charset=UTF-8",
    "origin": "https://finance.yahoo.com",
    "referer": "https://finance.yahoo.com",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
}

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

# Load existing data and determine the starting date
def load_existing_data():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        if not df.empty:
            # Get the latest date in the data
            last_date = df["date_published"].max()
            return datetime.strptime(last_date, "%Y_%m_%d"), df
    # Default to start from a predefined date if no file exists
    return datetime.strptime("2012_06_01", "%Y_%m_%d"), pd.DataFrame(columns=["date_published", "title"])

def calculate_start_time(date_str):
    date_obj = datetime.strptime(date_str, "%Y_%m_%d")
    date_obj = date_obj.replace(hour=9, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
    return int(date_obj.timestamp() * 1000)

# Fetch articles for all dates, handling pagination
def fetch_all_news(start_date):
    all_articles = []
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
                    save_to_csv(articles)
                    all_articles.extend(articles)
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

    return all_articles

# Save articles to a CSV file
def save_to_csv(articles):
    if os.path.exists(CSV_FILE):
        existing_df = pd.read_csv(CSV_FILE)
        new_df = pd.DataFrame(articles)
        updated_df = pd.concat([existing_df, new_df]).drop_duplicates(subset=["date_published", "title"])
    else:
        updated_df = pd.DataFrame(articles)
    updated_df.to_csv(CSV_FILE, index=False)
    print(f"Saved {len(articles)} new articles to {CSV_FILE}.")

# Main function
if __name__ == "__main__":
    print("Fetching Yahoo Finance articles...")
    start_date, _ = load_existing_data()
    start_date += timedelta(days=1)  # Start from the next day
    fetch_all_news(start_date)