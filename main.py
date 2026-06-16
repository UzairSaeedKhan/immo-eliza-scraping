from src.property_listings_scraper import scrape_all_provinces
from src.utils import save_to_csv
import requests
import time
import pandas as pd
from src.property_details_scraper import parse_features
from src.async_utils import scrape_all
import asyncio

"""
session = requests.Session()
base_url = "https://immovlan.be/en/real-estate"
common_params = {
    "transactiontypes": "for-sale,in-public-sale",
    "propertytypes": "house,apartment"
}
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

all_province_listings = scrape_all_provinces()
save_to_csv(all_province_listings, "./data/property_listings.csv")
"""

df = pd.read_csv("./data/property_listings.csv")
urls = df["property_url"].tolist()[:100]

results = asyncio.run(scrape_all(urls, parse_features, max_concurrent=10))

for i, r in enumerate(results):
    print(f"[{i+1}/{len(results)}]", r)