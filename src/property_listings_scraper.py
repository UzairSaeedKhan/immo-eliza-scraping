import requests, time, re
from bs4 import BeautifulSoup
import pandas as pd
import time, re

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
    "luxembourg",
]

def scrape_listings_by_province(session, province, target=1000, max_pages=50):
    results = []
    for page in range(1, max_pages + 1):
        params = {**common_params, "provinces": province, "page": page}

        try:
            r = session.get(base_url, params=params, headers=HEADERS, timeout=10)
            r.raise_for_status() 
        except requests.exceptions.RequestException as e:
            print(f"{province} page {page}: request failed -> {e}")
            break  # stopping for this province only rather than crashing the whole script

        soup = BeautifulSoup(r.text, "html.parser")

        property_cards = soup.select("article[data-url][itemtype$='Apartment'], article[data-url][itemtype$='House']")

        # if no more listings on this page then stop pagination for this province
        if not property_cards:
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

        time.sleep(1)

    print(f"{province}: collected {len(results)} listings")
    
    return results


def parse_listing_url(url):
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

start_time = time.time()  # start timer
all_listings = []
for prov in provinces:
    all_listings.extend(scrape_listings_by_province(session, prov))

end_time = time.time()  # end timer
print(f"The pipeline took {end_time-start_time} seconds")

# print(all_listings)
df = pd.DataFrame(all_listings)
df.to_csv("./../data/property_listings.csv", index=False)