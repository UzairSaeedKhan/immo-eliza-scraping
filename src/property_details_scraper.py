import re
from bs4 import BeautifulSoup
import json
from src.geo_utils import analyze_geo

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


def binary_element(label,soup):
    """
    Extract a binary feature from the property page.

    The function tries to convert textual property features into:
    - 1 = Yes
    - 0 = No
    - None = information not available

    It supports two possible HTML patterns:
    1. Structured <h4> blocks (preferred source)
    2. Fallback <strong> tags in unstructured text
    """    
    value = value_after_h4(label,soup)
    
    if value:
        value = value.lower().strip()
        if value == "yes":
            return 1
        if value == "no":
            return 0

    return None

def binary_vat_reader(label,soup):
    """
    Extract VAT-related binary information from the HTML.

    Returns:
        1 if VAT is mentioned as "yes"
        0 if VAT is mentioned as "no"
        None if no information is found
    """
    #Normalize label once (avoid repeated .lower() calls inside loop)
    label = label.lower()

    #Iterate over all <strong> tags (possible key-value indicators in the page)
    for strong in soup.find_all("strong"):

        strong_text = strong.get_text(strip=True).lower()

        #Check if this <strong> corresponds to the VAT label
        if label in strong_text:

            text = strong.parent.get_text(" ", strip=True).lower()

            if "yes" in text:
                return 1

            if "no" in text:
                return 0

    return None

def get_description(soup):
    """
    Take the description of the property
    """
    description_div = soup.find("div", class_="dynamic-description")

    if description_div:
        return description_div.get_text(separator="\n", strip=True)

    return None

def get_distance(category, mode,soup):
    """
    Extract distance information for a given category (e.g. Train stations)
    and transport mode (e.g. Walking, Driving).

    Returns:
        Distance in meters as float if found,
        otherwise None.
    """
    for block in soup.find_all("div", class_="data-row"):
        h3 = block.find("h3")
        if h3 and category in h3.get_text():
            span = block.find("span", title=mode)
            if span:
                parts = span.get_text(strip=True).split()
                distance = float(parts[0])
                if parts[1] == "km":
                    distance *= 1000
                return distance
    return None
    
    
def get_latitude(soup):
    #"""
    #Extract latitude value from embedded JSON scripts in the HTML.

    #Returns:
    #    float latitude if found, otherwise None
    #"""

    for script in soup.find_all("script"):
        try:
            data = json.loads(script.string)
            lat = data["latitude"]
            return float(lat)
        except:
            continue
    return None
    
def get_longitude(soup):
    """
    Extract longitude value from embedded JSON scripts in the HTML.

    Returns:
        float longitude if found, otherwise None
    """
    for script in soup.find_all("script"):
        try:
            data = json.loads(script.string)
            lon = data["longitude"]
            return float(lon)
        except:
            continue
    return None

    
def parse_features(html):
    """
    Extracts key property listing details from the HTML page:

    - Energy Performance Certificate (EPC) rating.
    - Advertised property price, cleaned and normalized from the displayed format.
    - Unique property listing identifier (Property ID / Vlan Code).

    The extracted data is intended for storage, analysis, or further processing.
    """
    soup = BeautifulSoup(html, "html.parser")
    meta_desc = soup.find("meta", attrs={"name": "description"})
    
    #EPC score
    epc = None
    if meta_desc:
        description = meta_desc.get("content", "")
        match = re.search(r"EPC\s+([A-G]\+?)", description)
        if match:
            epc = match.group(1)

   
    #Price
    price_raw = soup.find("span", class_="detail__header_price_data")
    if price_raw:
        raw_text = price_raw.get_text(strip=True)
        digits = "".join(c for c in raw_text if c.isdigit())
        price = float(digits) if digits else None
    
    #Property ID
    property_id = soup.find("span", class_ = "vlancode").get_text(strip=True)
    
    #Geography
    #lat = get_latitude(soup)
    #lon = get_longitude(soup)
    #postal_code = None #TO REMOVE!
    #geo_info = analyze_geo(lat, lon, postal_code)

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
        #**geo_info, 
        
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
        
        "distance_from_train_stations_by_foot_in_m": get_distance("Train stations", "Walking",soup),
        "distance_from_train_stations_by_car_in_m": get_distance("Train stations", "Driving",soup),
        "distance_from_motorway_by_car_in_m": get_distance("Motorways", "Driving",soup),
        "distance_from_bus_by_foot_in_m": get_distance("Bus", "Walking",soup),
        "distance_from_tram_by_foot_in_m": get_distance("Trams", "Walking",soup),
        "distance_from_metro_by_foot_in_m": get_distance("Metros", "Walking",soup),
        "distance_from_nursery_by_foot_in_m": get_distance("Nurseries", "Walking",soup),
        "distance_from_nursery_by_car_in_m": get_distance("Nurseries", "Driving",soup),
        "distance_from_preschool_by_foot_in_m": get_distance("Preschools", "Walking",soup),
        "distance_from_preschool_by_car_in_m": get_distance("Preschools", "Driving",soup),
        "distance_from_elementary_school_by_foot_in_m": get_distance("Elementary schools", "Walking",soup),
        "distance_from_elementary_school_by_car_in_m": get_distance("Elementary schools", "Driving",soup),
        "distance_from_high_school_by_foot_in_m": get_distance("High schools", "Walking",soup),
        "distance_from_high_school_by_car_in_m": get_distance("High schools", "Driving",soup),
        "distance_from_supermarket_by_foot_in_m": get_distance("Supermarkets", "Walking",soup),
        "distance_from_supermarket_by_car_in_m": get_distance("Supermarkets", "Driving",soup),
        "distance_from_supermarket_by_transports_in_m": get_distance("Supermarkets", "Transit",soup),
        "distance_from_supermarket_by_car_in_m": get_distance("Supermarkets", "Driving",soup),
        
        "description" : get_description(soup)
    }
    return tags