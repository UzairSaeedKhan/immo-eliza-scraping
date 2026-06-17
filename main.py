from src.property_listings_scraper import scrape_all_provinces
from src.utils import save_to_csv, join_two_dfs_by_property_id
from src.property_details_scraper import parse_features
from src.async_utils import scrape_all
import asyncio
import polars as pl

property_listings_df = asyncio.run(scrape_all_provinces())
save_to_csv(property_listings_df, "./data/property_listings.csv")

property_listings_df = pl.read_csv("./data/property_listings.csv")
urls = property_listings_df["property_url"].to_list()[:100]

property_details = asyncio.run(scrape_all(urls, parse_features, max_concurrent=10))
property_details_df = pl.DataFrame(property_details)[:100]

joined_df = join_two_dfs_by_property_id(property_listings_df, property_details_df)
save_to_csv(joined_df, "./data/scraped_sample_properties.csv") # let it be like "scraped_sample_properties" until we are sure everythings working
