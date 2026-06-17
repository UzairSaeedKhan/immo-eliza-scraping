import requests, re
from bs4 import BeautifulSoup
import json
import requests #API part
import math

#url = "https://immovlan.be/en/detail/residence/for-sale/6040/jumet/vbe35169"
url = "https://immovlan.be/en/detail/residence/for-sale/1150/sint-pieters-woluwe/vbe35189"
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

                    if parts[1] == "km": #peut etre garder pour le "by car" et mettre en "m" uniquement pour foot
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
    
    #Property id
    property_id = soup.find("span", class_ = "vlancode").get_text(strip=True)


    def get_postal_code():
        city = soup.find("span", class_="city-line")

        if not city:
            return None

        digits = "".join(c for c in city.get_text() if c.isdigit())

        if len(digits) == 4:
            return int(digits)

        return None
    postal_code = get_postal_code()


    #DISTANCE API

    def get_distance_to_brussels(soup, lon, postal_code):
        """
        Returns:
        - 0 if already in Brussels (based on postal code)
        - driving distance in km otherwise (OSRM)
        - None if data missing
        """

        # -----------------------------
        # 2. Brussels postal codes check
        # -----------------------------
        brussels_postcodes = {
            1000, 1020, 1030, 1040, 1050,
            1060, 1070, 1080, 1081, 1082,
            1083, 1090, 1140, 1150,
            1160, 1170, 1180, 1190
        }

        if postal_code in brussels_postcodes:
            return 0

        # -----------------------------
        # 3. Check coordinates
        # -----------------------------
        if lat is None or lon is None:
            return None

        # -----------------------------
        # 4. OSRM request
        # -----------------------------
        brussels_lat = 50.8501
        brussels_lon = 4.3634

        url = (
            "http://router.project-osrm.org/route/v1/driving/"
            f"{lon},{lat};{brussels_lon},{brussels_lat}"
            "?overview=false"
        )

        try:
            response = requests.get(url, timeout=5)
            data = response.json()

            distance_m = data["routes"][0]["distance"]

            return round(distance_m / 1000, 2)

        except:
            return None
    lat = get_latitude()
    lon = get_longitude()

    #DISTANCE CHEF LIEU 
    def get_distance_to_nearest_capital(lat, lon, postal_code):

        if lat is None or lon is None:
            return None, None

        capitals = {
            "Brussels": (50.8501, 4.3634),
            "Antwerp": (51.2194, 4.4025),
            "Ghent": (51.0543, 3.7174),
            "Bruges": (51.2093, 3.2247),
            "Hasselt": (50.9307, 5.3325),
            "Leuven": (50.8798, 4.7005),
            "Mons": (50.4542, 3.9523),
            "Namur": (50.4674, 4.8718),
            "Liège": (50.6326, 5.5797),
            "Arlon": (49.6833, 5.8167)
        }

        capital_postcodes = {
            "Brussels": {1000, 1020, 1030, 1040, 1050, 1060, 1070, 1080, 1081, 1082, 1083, 1090},
            "Antwerp": {2000, 2018, 2020, 2030, 2040, 2050},
            "Ghent": {9000, 9030, 9031, 9032, 9040, 9041, 9042, 9050},
            "Bruges": {8000, 8200, 8310, 8370, 8380},
            "Hasselt": {3500, 3510, 3520, 3530},
            "Leuven": {3000, 3010, 3020, 3050},
            "Mons": {7000, 7011, 7012, 7020, 7030},
            "Namur": {5000, 5100, 5101, 5102},
            "Liège": {4000, 4020, 4030, 4040, 4050},
            "Arlon": {6700, 6704, 6706, 6717}
        }
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371
            lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
            return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))

        # 1. trouver la capitale "du logement" (si elle existe)
        property_capital = None
        if postal_code is not None:
            for city, codes in capital_postcodes.items():
                if postal_code in codes:
                    property_capital = city
                    break

        # 2. calcul distances
        distances = []
        for city, (c_lat, c_lon) in capitals.items():
            d = haversine(lat, lon, c_lat, c_lon)
            distances.append((city, d))

        # 3. tri
        distances.sort(key=lambda x: x[1])

        # 4. exclusion propre de la capitale du logement
        filtered = []
        for city, dist in distances:
            if city != property_capital:
                filtered.append((city, dist))

        # 5. résultat final
        if len(filtered) == 0:
            return None, None

        nearest_city, nearest_distance = filtered[0]

        return round(nearest_distance, 2), nearest_city
        
        
    distance, nearest_city = get_distance_to_nearest_capital(lat, lon, postal_code)

    #Results
    Tags = {
    
        "price_in_€" : price,
        "vat_included" : binary_element("VAT"),
        
        "state_of_property" : get_state_of_property(),
        "livable_surface" : value_after_h4("Surface"),
        "construction_year" : value_after_h4("Build Year"),
        "epc_score" : epc,

        "latitude" : get_latitude(),
        "longitude" : get_longitude(),
        "distance_to_brussels_in_km_by_car": get_distance_to_brussels(soup, lon, postal_code),
        "nearest_capital": nearest_city,
        "distance_to_nearest_capital_km": distance, 
        

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
        "distance_from_train_stations_by_car_in_m": get_train_distance("Driving")}
    

    for key, value in Tags.items():
        print(f"- {key}: {value if value is not None else 'No information on Immovlan website'}, {type(value)}")
        
parse_features(url)
