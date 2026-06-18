from src.property_listings_scraper import scrape_all_provinces
from src.utils import save_to_csv, join_two_dfs_by_property_id
from src.property_details_scraper import parse_features
from src.async_utils import scrape_all
import asyncio
import polars as pl
from codecarbon import track_emissions

@track_emissions(output_dir="./data")
def main():
    """
    Pipeline:
    Scrape property listings (async, all provinces)
    Save listings to property_listings.csv
    Reload listings CSV and extract property URLs
    Scrape property details for each URL (async)
    Join listings + details on property_id
    Export final dataset to scraped_properties.csv
    """ 

    property_listings_df = asyncio.run(scrape_all_provinces())
    save_to_csv(property_listings_df, "./data/property_listings.csv")

    # uncomment this line when you want to use the old property_listings csv
    # property_listings_df = pl.read_csv("./data/property_listings.csv")
    urls = property_listings_df["property_url"].to_list()

    property_details = asyncio.run(scrape_all(urls, parse_features, max_concurrent=10))
    property_details_df = pl.DataFrame(property_details)

    joined_df = join_two_dfs_by_property_id(property_listings_df, property_details_df)
    save_to_csv(joined_df, "./data/scraped_properties.csv")

if __name__ == "__main__":
    main()