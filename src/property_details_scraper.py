import re
from bs4 import BeautifulSoup
import json


def value_after_h4(label,soup):
    """
    Extracts the value associated with a given <h4> label
    Example:
    # <h4>Number of bedrooms</h4>
    # <p>3</p>
    # returns -> 3
    """
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
        return int(float(value)) #improvement
    return value 

def get_property_info(section_title, field_name,soup):
    """
    Extract a specific field value from a given property section
    on the Immovlan webpage.

    The function searches inside structured "data-row" blocks,
    identifies the correct section via its <h3> title, then retrieves
    the corresponding field value from <h4> / <p> pairs.

    Returns:
        str or None: The extracted value if found, otherwise None.
    """
    section_title = section_title.lower()
    field_name = field_name.lower()
     
    for block in soup.find_all("div", class_="data-row"):
        h3 = block.find("h3")
        if not h3:
            continue

        if section_title.lower() not in h3.get_text(" ", strip=True).lower():
            continue
     
        for item in block.find_all("div"):
            h4 = item.find("h4")
            p = item.find("p")
            if h4 and field_name.lower() in h4.get_text(strip=True).lower():
                return p.get_text(strip=True) if p else None
    return None

#converts "Yes" in 1 and "No" in 0 (None if no infos) 
def binary_element(label,soup):    
    value = value_after_h4(label,soup)
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
   

    

#Train station distance storing
def get_train_distance(mode,soup):
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
    
    
def get_latitude(soup):
    for script in soup.find_all("script"):
        try:
            data = json.loads(script.string)
            lat = data["latitude"]
            return float(lat)
        except:
            continue
    return None
    
def get_longitude(soup):
    for script in soup.find_all("script"):
        try:
            data = json.loads(script.string)
            lon = data["longitude"]
            return float(lon)
        except:
            continue
    return None
    
    


#Global function contains all the functions related to scraping data
def parse_features(html):
    soup = BeautifulSoup(html, "html.parser")
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
    property_id = soup.find("span", class_ = "vlancode").get_text(strip=True)
    
    tags = {
        "property_id": property_id,
        "price_in_€" : price,
        "vat_included" : binary_element("VAT",soup),  
        "state_of_property" : get_property_info("General info", "State of the property", soup),
        "heating_type" : get_property_info("Heating and energy","Type of heating",soup),
        "sun_exposure" : get_property_info("Outdoor description","Orientation of the front facade", soup),
        "livable_surface_in_m²" : value_after_h4("Surface", soup),
        "construction_year" : value_after_h4("Build Year",soup),
        "epc_score" : epc,
        "latitude" : get_latitude(soup),
        "longitude" : get_longitude(soup), 
        "furnished" : binary_element("Furnished",soup),    
        "nb_of_facades" : value_after_h4("Number of facades",soup),
        "nb_of_floors" : value_after_h4("Number of floors",soup),
        "nb_of_bedrooms" : value_after_h4("Number of bedrooms",soup),
        "nb_of_bathrooms" : value_after_h4("Number of bathrooms",soup),
        "nb_of_showers" : value_after_h4("Number of showers",soup),
        "nb_of_toilets" : value_after_h4("Number of toilets",soup),    
        "terrace" : binary_element("Terrace",soup),
        "veranda" : binary_element("Veranda",soup),
        "elevator" : binary_element("Elevator",soup),
        "access_for_disabled" : binary_element("Access for disabled",soup),
        "garden" : binary_element("Garden",soup),
        "garage" : binary_element("Garage",soup), 
        "swimming_pool" : binary_element("Swimming pool",soup), 
        "cellar" : binary_element("Cellar",soup), 
        "attic" : binary_element("Attic",soup),
        "flooding_area_type" : get_property_info("Town planning and environmental risks", "flooding area type",soup),   
        "distance_from_train_stations_by_foot_in_m": get_train_distance("Walking",soup),
        "distance_from_train_stations_by_car_in_m": get_train_distance("Driving",soup)
    }
    return tags



    # for key, value in Tags.items():
    #     print(f"- {key}: {value if value is not None else 'No information on Immovlan website'}, {type(value)}")