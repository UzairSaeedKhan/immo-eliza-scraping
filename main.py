from src.property_listings_scraper import scrape_all_provinces
from src.utils import save_to_csv, join_two_dfs_by_property_id
from src.property_details_scraper import parse_features
from src.async_utils import scrape_all
import asyncio
import polars as pl

all_province_listings = scrape_all_provinces()
save_to_csv(all_province_listings, "./data/property_listings.csv")

property_listings_df = pl.read_csv("./data/property_listings.csv")
urls = property_listings_df["property_url"].to_list()

property_details = asyncio.run(scrape_all(urls, parse_features, max_concurrent=10))
property_details_df = pl.DataFrame(property_details)

joined_df = join_two_dfs_by_property_id(property_listings_df, property_details_df)
joined_df.write_csv("./data/scraped_properties.csv")
