import re
from bs4 import BeautifulSoup
import json

#Global function contains all the functions related to scraping data
def parse_features(html):
    soup = BeautifulSoup(html, "html.parser")
    #Take the value after h4 in the HTML file (the <p> block)
    def value_after_h4(label):
        h4 = soup.find("h4", string=lambda x: x and label.lower() in x.lower())
        if not h4:
            return None
        block = h4.find_parent()
        texts = block.stripped_strings
        next(texts, None)
        value = next(texts, None)
        if not value:
            return None
        value = value.replace("m²", "").strip()
        # conversion seulement si c'est un nombre
        if value.replace(".", "", 1).isdigit():
            if "." in value:
                return float(value)
            return float(value)
        return value    
    
    def get_state_of_property():
        blocks = soup.find_all("div", class_="data-row")
        for block in blocks:
            h3 = block.find("h3")
            if not h3:
                continue

            if "General info" not in h3.get_text(" ", strip=True):
                continue
            items = block.find_all("div")
            for item in items:
                h4 = item.find("h4")
                p = item.find("p")
                if h4 and "state of the property" in h4.get_text(strip=True).lower():
                    return p.get_text(strip=True) if p else None
        return None

    #converts "Yes" in 1 and "No" in 0 (None if no infos) 
    def binary_element(label):    
        value = value_after_h4(label)
        #infos in h4 blocks
        if value:
            value = value.lower().strip()
            if value == "yes":
                return 1
            if value == "no":
                return 0

        #infos in other blocks than h4 (ex: <strong>)
        for tag in soup.find_all(string=True):
            if label.lower() in tag.lower():
                text = tag.parent.parent.get_text(" ", strip=True).lower()
                if "yes" in text:
                    return 1
                if "no" in text:
                    return 0
        return 0
   

    #EPC score storing
    meta_desc = soup.find("meta", attrs={"name": "description"})
    epc = None
    if meta_desc:
        description = meta_desc.get("content", "")
        match = re.search(r"EPC\s+([A-G]\+?)", description)
        if match:
            epc = match.group(1)

    """
    #To store and clean the price
    price_raw = soup.find("span", class_="detail__header_price_data")

    if price_raw:
        price = price_raw.get_text(strip=True)
        price = price.replace("\u202f", "")
        price = price.replace("€", "")
        price = int(price.strip())

    else:
        price = None
    """
    price_raw = soup.find("span", class_="detail__header_price_data")

    if price_raw:
        price = price_raw.get_text(strip=True)
        # garde uniquement les chiffres
        price = "".join(c for c in price if c.isdigit())
        price = float(price) if price else None
    else:
        price = None

    #Train station distance storing
    def get_train_distance(mode):
        for block in soup.find_all("div", class_="data-row"):
            h3 = block.find("h3")
            if h3 and "Train stations" in h3.get_text():
                span = block.find("span", title=mode)
                if span:
                    parts = span.get_text(strip=True).split()
                    distance = float(parts[0])
                    if parts[1] == "km":
                        distance *= 1000
                    return distance
        return None
    
    
    def get_latitude():
        for script in soup.find_all("script"):
            try:
                data = json.loads(script.string)
                lat = data["latitude"]
                return float(lat)
            except:
                continue
        return None
    
    def get_longitude():
        for script in soup.find_all("script"):
            try:
                data = json.loads(script.string)
                lon = data["longitude"]
                return float(lon)
            except:
                continue
        return None
    
    def get_flooding():
        blocks = soup.find_all("div", class_="data-row")
        for block in blocks:
            h3 = block.find("h3")
            if not h3:
                continue
            if "Town planning and environmental risks" not in h3.get_text(" ", strip=True):
                continue
            items = block.find_all("div")
            for item in items:
                h4 = item.find("h4")
                p = item.find("p")
                if h4 and "flooding area type" in h4.get_text(strip=True).lower():
                    return p.get_text(strip=True) if p else None
        return None
    
    property_id = soup.find("span", class_ = "vlancode").get_text(strip=True)

    tags = {
        "property_id": property_id,
        "price_in_€" : price,
        "vat_included" : binary_element("VAT"),  
        "state_of_property" : get_state_of_property(),
        "livable_surface" : value_after_h4("Surface"),
        "construction_year" : value_after_h4("Build Year"),
        "epc_score" : epc,
        "latitude" : get_latitude(),
        "longitude" : get_longitude(), 
        "furnished" : binary_element("Furnished"),    
        "nb_of_facades" : value_after_h4("Number of facades"),
        "nb_of_floors" : value_after_h4("Number of floors"),
        "nb_of_bedrooms" : value_after_h4("Number of bedrooms"),
        "nb_of_bathrooms" : value_after_h4("Number of bathrooms"),
        "nb_of_showers" : value_after_h4("Number of showers"),
        "nb_of_toilets" : value_after_h4("Number of toilets"),    
        "terrace" : binary_element("Terrace"),
        "veranda" : binary_element("Veranda"),
        "elevator" : binary_element("Elevator"),
        "access_for_disabled" : binary_element("Access for disabled"),
        "garden" : binary_element("Garden"),
        "garage" : binary_element("Garage"), 
        "swimming_pool" : binary_element("Swimming pool"), 
        "cellar" : binary_element("Cellar"), 
        "attic" : binary_element("Attic"),
        "flooding_area_type" : get_flooding(),   
        "distance_from_train_stations_by_foot_in_m": get_train_distance("Walking"),
        "distance_from_train_stations_by_car_in_m": get_train_distance("Driving")
    }
    return tags
    

    # for key, value in Tags.items():
    #     print(f"- {key}: {value if value is not None else 'No information on Immovlan website'}, {type(value)}")
