import json
from scraper import scrape
from data_cleaner import clean_data
from output import to_csv, to_google_sheets

if __name__ == "__main__":
    with open("config.json", "r") as f:
        config = json.load(f)

    print("Scraping started...")
    raw_data = scrape(config)
    cleaned_data = clean_data(raw_data)
    to_csv(cleaned_data)
    to_google_sheets(cleaned_data)
    print("Scraping finished.")
