import asyncio, httpx, time, re
from bs4 import BeautifulSoup
import polars as pl
import time, re

base_url = "https://immovlan.be/en/real-estate"
common_params = {
    "transactiontypes": "for-sale,in-public-sale",
    "propertytypes": "house,apartment"
}
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

async def scrape_listings_by_province(client, semaphore, province, target=1000, max_pages=50) -> list:
    """
    Paginate through Immovlan's listing search results for a single province,
    collecting property URLs and a few fields parsed from each URL until either
    'target' listings are collected or 'max_pages' is reached.
 
    Runs as one "task" among many in scrape_all_provinces(); the semaphore is
    shared across all provinces to cap total concurrent requests.
    """

    results = []
    for page in range(1, max_pages + 1):
        params = {**common_params, "provinces": province, "page": page}

        try:
            async with semaphore:
                r = await client.get(base_url, params=params, headers=HEADERS, timeout=10)
            r.raise_for_status() 
        except httpx.RequestError as e:
            print(f"{province} page {page}: request failed -> {e}")
            break  # stopping for this province only rather than crashing the whole script

        soup = BeautifulSoup(r.text, "html.parser")

        all_cards = soup.select("article[data-url]")
        property_cards = soup.select("article[data-url][itemtype$='Apartment'], article[data-url][itemtype$='House']")

        # if no more listings on this page then stop pagination for this province
        if not all_cards:
            break  

        for card in property_cards:
            url = card.get("data-url")
            itemtype = card.get("itemtype")
            type_property = itemtype.rsplit("/", 1)[-1] if itemtype else None
            if url:
                parsed = parse_listing_url(url)
                results.append({
                    "province": province,
                    "type_property": type_property,
                    "property_url": url,
                    **parsed
                })
            else:
                print(f"{province} page {page}: card with no data-url, so it is skipped")

        if len(results) >= target:
            results = results[:target]
            break

        await asyncio.sleep(1)

    print(f"{province}: collected {len(results)} listings")
    
    return results


def parse_listing_url(url):
    """
    Extract structured fields out of an Immovlan listing URL, e.g.:
    /detail/<subtype>/<contract>/<postal_code>/<city>/<property_id>
 
    Returns a dict of Nones if the URL doesn't match the expected shape.
    """

    URL_PATTERN = re.compile(
    r"/detail/(?P<subtype>[^/]+)/(?P<contract>[^/]+)/(?P<postal_code>\d+)/(?P<city>[^/]+)/(?P<property_id>[^/]+)"
    )
    match = URL_PATTERN.search(url)
    if not match:
        print(f"URL didn't match expected pattern, skipping fields: {url}")
        return {
            "property_id": None,
            "subtype_property": None,
            "type_of_contract": None,
            "postal_code": None,
            "city": None,
        }
    return {
        "property_id": match.group("property_id"),
        "subtype_property": match.group("subtype"),
        "type_of_contract": "sale" if "sale" in match.group("contract") else match.group("contract"), # will change this to rent if we do it
        "postal_code": match.group("postal_code"),
        "city": match.group("city"),
    }

async def scrape_all_provinces() -> pl.DataFrame:
    """
    Top-level entry point: fan out scrape_listings_by_province() across all
    Belgian provinces + Brussels concurrently, then flatten the
    results into a single Polars DataFrame.
 
    Concurrency is controlled by a single shared semaphore.
    """

    provinces = [
    "brussels", "vlaams-brabant", "antwerp", "east-flanders", "west-flanders",
    "brabant-wallon", "limburg", "hainaut", "namur", "liege", "luxembourg" 
    ]
    semaphore = asyncio.Semaphore(10)
    start_time = time.time()
    async with httpx.AsyncClient(headers = HEADERS) as client:
        tasks = [scrape_listings_by_province(client, semaphore, prov) for prov in provinces]
        results = await asyncio.gather(*tasks) 
    end_time = time.time()
    print(f"The scrape_all_provinces pipeline took {(end_time-start_time)/60} minutes")
    return pl.DataFrame([listing for prov_results in results for listing in prov_results])