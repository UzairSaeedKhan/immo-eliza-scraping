import requests, re
from bs4 import BeautifulSoup
import json
import requests #API part
import math

#url = "https://immovlan.be/en/detail/residence/for-sale/6040/jumet/vbe35169"
url = "https://immovlan.be/en/detail/apartment/for-sale/3020/herent/rbw18421"
#url = "https://immovlan.be/en/detail/residence/for-sale/3550/heusden-zolder/rbw24745"
#url ="https://immovlan.be/en/detail/student-flat/for-sale/3000/leuven/rbw24627"


#Global function contains all the functions related to scraping data
def parse_features(url):
    #soup = BeautifulSoup(url, "html.parser")
    html = requests.get(
        url,
        headers={"User-agent": "Mozilla/5.0"}
    ).text

    soup = BeautifulSoup(html, "html.parser")

#--------------------------------------------------------------------------------------------------------    
    #Take the value after h4 in the HTML file (the <p> block)
    def value_after_h4(label):
        """
        Extracts the value associated with a given <h4> label
        Example:
        # <h4>Number of bedrooms</h4>
        # <p>3</p>
        # returns -> 3
        """
        #Convert once to avoid repeated lower() calls
        label = label.lower() #improvement: call label.lower() earlier (improve the carbone emission apparently)

        #Find the matching h4 element
        h4 = soup.find("h4", string=lambda x: x and label in x.lower())

        if not h4:
            return None

        #Get the parent block containing both the label and its value
        block = h4.parent #improvement : removing "find.parent()" to know go through more element than necessary

        #Retrieve all non-empty text elements from the block
        texts = block.stripped_strings

        #Skip the label itself
        next(texts, None)

        #Get the value located after the label
        value = next(texts, None)

        if not value:
            return None

        #Remove unit if present
        value = value.replace("m²", "").strip()

        #Convert numeric values to integers
        if value.replace(".", "", 1).isdigit():
            return int(float(value)) #improvement
            
        #Return text values unchanged
        return value    
    
#--------------------------------------------------------------------------------------------------------    
    def get_property_info(section_title, field_name):
        """
        Extract a specific field value from a given property section
        on the Immovlan webpage.

        The function searches inside structured "data-row" blocks,
        identifies the correct section via its <h3> title, then retrieves
        the corresponding field value from <h4> / <p> pairs.

        Returns:
            str or None: The extracted value if found, otherwise None.
        """

        #Convert search strings once to avoid repeated lower() calls
        section_title = section_title.lower()
        field_name = field_name.lower()

        #Browse all information sections of the property page
        for block in soup.find_all("div", class_="data-row"): #improvement: removing blocks

            h3 = block.find("h3")

            #Skip blocks without a section title
            if not h3:
                continue

            # Check if this is the section we are looking for
            if section_title.lower() not in h3.get_text(" ", strip=True).lower():
                continue
            
            #Search inside the matching section
            for item in block.find_all("div"): #improvement: removing items

                
                h4 = item.find("h4")
                p = item.find("p")

                #If the field matches, return its associated value
                if h4 and field_name.lower() in h4.get_text(strip=True).lower():
                    return p.get_text(strip=True) if p else None
                
        #Information not found
        return None

#--------------------------------------------------------------------------------------------------------    
   
    def binary_element(label):    
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

        #Try to extract value from standard <h4> structure
        value = value_after_h4(label)

        if value:
            value = value.lower().strip()

            if value.startswith("yes"):
                return 1
            if value.startswith("no"):
                return 0
        #improvement : removing the strong part

        #No information found
        return None
#--------------------------------------------------------------------------------------------------------    

    def binary_vat_reader(label):
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
    
   
#--------------------------------------------------------------------------------------------------------    

    # Extract EPC rating from the page meta description
    # Example format: "EPC A, some other text..."
    meta_desc = soup.find("meta", attrs={"name": "description"})

    epc = None

    if meta_desc:
        #Get meta description content safely
        description = meta_desc.get("content", "")

        #Search for EPC pattern (A-G or A+ style rating)
        match = re.search(r"EPC\s+([A-G]\+?)", description)

        #Extract EPC value if pattern is found
        if match:
            epc = match.group(1)

#--------------------------------------------------------------------------------------------------------    
    #Extract property price from HTML and clean it into a numeric value
    price_raw = soup.find("span", class_="detail__header_price_data")

    price = None #improvement

    if price_raw: #improvement
        #Get raw price and remove spaces/€ symbols in one step
        raw_text = price_raw.get_text(strip=True)

        #Keep only digits (remove currency symbols, spaces, etc.)
        digits = "".join(c for c in raw_text if c.isdigit())

        #Convert to float if valid, otherwise keep None
        price = float(digits) if digits else None



#--------------------------------------------------------------------------------------------------------    

    def get_distance(category, mode):
        """
        Extract distance information for a given category (e.g. Train stations)
        and transport mode (e.g. Walking, Driving).

        Returns:
            Distance in meters as float if found,
            otherwise None.
        """
        

        #Loop through all property sections
        for block in soup.find_all("div", class_="data-row"):

            #Extract section title (e.g. "Train stations", "Bus", etc.)
            h3 = block.find("h3")

            #Match category
            if h3 and category in h3.get_text():

                #Find the distance element for the requested mode
                span = block.find("span", title=mode)

                if span:
                    parts = span.get_text(strip=True).split()

                    distance = float(parts[0])

                    #Convert kilometers to meters if needed
                    if parts[1] == "km":
                        distance *= 1000

                    return distance

        return None
    
  #--------------------------------------------------------------------------------------------------------    
  
    def get_latitude():
        """
        Extract latitude value from embedded JSON scripts in the HTML.

        Returns:
            float latitude if found, otherwise None
        """
        #Loop through all <script> tags in the page
        for script in soup.find_all("script"):
            
            try:
                #Try to parse JSON content inside script
                data = json.loads(script.string)

                #Extract latitude if available
                lat = data["latitude"]
                
                return float(lat)

            except:
                #Ignore scripts that are not valid JSON or missing keys
                continue

        return None

#--------------------------------------------------------------------------------------------------------    

    def get_longitude():
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
    
 #--------------------------------------------------------------------------------------------------------    
    # Extract the unique property identifier (vlancode) from the HTML page
    # This ID is used to uniquely reference the property listing
    property_id = soup.find("span", class_ = "vlancode").get_text(strip=True)

#--------------------------------------------------------------------------------------------------------    

    #Results
    Tags = {
    
        "price_in_€" : price,
        "vat_included" : binary_vat_reader("VAT"),
        
        "state_of_property" : get_property_info("General info", "State of the property"),
        "heating_type" : get_property_info("Heating and energy","Type of heating"),
        "sun_exposure" : get_property_info("Outdoor description","Orientation of the front facade"),
        "livable_surface_in_m²" : value_after_h4("Surface"),
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

        "flooding_area_type" : get_property_info("Town planning and environmental risks", "flooding area type"),
        
        "distance_from_train_stations_by_foot_in_m": get_distance("Train stations", "Walking"),
        "distance_from_train_stations_by_car_in_m": get_distance("Train stations", "Driving"),
        "distance_from_motorway_by_car_in_m": get_distance("Motorways", "Driving"),
        "distance_from_bus_by_foot_in_m": get_distance("Bus", "Walking"),
        "distance_from_tram_by_foot_in_m": get_distance("Trams", "Walking"),
        "distance_from_metro_by_foot_in_m": get_distance("Metros", "Walking"),
        "distance_from_nursery_by_foot_in_m": get_distance("Nurseries", "Walking"),
        "distance_from_nursery_by_car_in_m": get_distance("Nurseries", "Driving"),
        "distance_from_preschool_by_foot_in_m": get_distance("Preschools", "Walking"),
        "distance_from_preschool_by_car_in_m": get_distance("Preschools", "Driving"),
        "distance_from_elementary_school_by_foot_in_m": get_distance("Elementary schools", "Walking"),
        "distance_from_elementary_school_by_car_in_m": get_distance("Elementary schools", "Driving"),
        "distance_from_high_school_by_foot_in_m": get_distance("High schools", "Walking"),
        "distance_from_high_school_by_car_in_m": get_distance("High schools", "Driving"),
        "distance_from_supermarket_by_foot_in_m": get_distance("Supermarkets", "Walking"),
        "distance_from_supermarket_by_car_in_m": get_distance("Supermarkets", "Driving"),
        "distance_from_supermarket_by_transports_in_m": get_distance("Supermarkets", "Transit"),
        "distance_from_supermarket_by_car_in_m": get_distance("Supermarkets", "Driving")
        }
    

    for key, value in Tags.items():
        print(f"- {key}: {value if value is not None else 'None'}, {type(value)}")
        
parse_features(url)

