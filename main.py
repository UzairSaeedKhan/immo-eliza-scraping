from src.property_listings_scraper import scrape_listings_by_province
import requests
import time
import pandas as pd

session = requests.Session()
base_url = "https://immovlan.be/en/real-estate"
common_params = {
    "transactiontypes": "for-sale,in-public-sale",
    "propertytypes": "house,apartment"
}
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

provinces = [
    "brussels", "vlaams-brabant", "antwerpen", "east-flanders",
    "west-flanders", "limburg", "hainaut",
    "namur", "liege", 
    "luxembourg", "brabant-wallon"
]

start_time = time.time()  # start timer
all_listings = []
for prov in provinces:
    all_listings.extend(scrape_listings_by_province(session, prov))

end_time = time.time()  # end timer
print(f"The pipeline took {end_time-start_time} seconds")

# print(all_listings)
df = pd.DataFrame(all_listings)
df.to_csv("data/property_listings.csv", index=False)