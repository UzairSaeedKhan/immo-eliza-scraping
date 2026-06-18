import math
import requests
from bs4 import BeautifulSoup
import json

#url = "https://immovlan.be/en/detail/duplex/for-sale/1000/brussels/vbe35095"

major_cities = {
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

major_cities_postcodes = {
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

#def fetch_soup(url):
    
#    html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text
#    return BeautifulSoup(html, "html.parser")

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0088

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    return 2 * R * math.asin(math.sqrt(a))

def distance_to_brussels(lat, lon):
    return round(haversine(lat, lon, *major_cities["Brussels"]), 2)
    """
    Returns:
    - 0 if already in Brussels (based on postal code)
    - driving distance in km otherwise (OSRM)
    - None if data missing
    """

#def get_latitude(soup):
    """
    Extract latitude value from embedded JSON scripts in the HTML.

    Returns:
        float latitude if found, otherwise None
    """
#    for script in soup.find_all("script"):
#        try:
#            data = json.loads(script.string)
#            lat = data["latitude"]
#            return float(lat)
#        except:
#            continue
#    return None
    
#def get_longitude(soup):
    """
    Extract longitude value from embedded JSON scripts in the HTML.

    Returns:
        float longitude if found, otherwise None
    """
#    for script in soup.find_all("script"):
#        try:
#            data = json.loads(script.string)
#            lon = data["longitude"]
#            return float(lon)
#        except:
#            continue
#    return None



#def extract_postal_code(soup):
    """
    Essaie de récupérer le code postal dans la page
    (méthode simple basée sur recherche texte)
    """
#    text = soup.get_text()

#    for i in range(1000, 9999):
#        if str(i) in text:
#            return i

#    return None

def detect_city_from_postal(postal_code):
    if postal_code is None:
        return None

    for city, codes in major_cities_postcodes.items():
        if postal_code in codes:
            return city

    return None

    
def nearest_capital(lat, lon, exclude_city=None):
    """Trouve la capitale la plus proche (hors ville exclue)"""
    best_city = None
    best_dist = float("inf")

    for city, (c_lat, c_lon) in major_cities.items():

        if city == exclude_city:
            continue

        d = haversine(lat, lon, c_lat, c_lon)

        if d < best_dist:
            best_dist = d
            best_city = city

    return best_city, round(best_dist, 2)
"""    
def analyze_property(url):
    
    #Fonction principale :
    #- extrait les données
    #- calcule distances
    #- applique la règle métier
    

    soup = fetch_soup(url)

    lat = get_latitude(soup)
    lon = get_longitude(soup)
    postal_code = extract_postal_code(soup)

    if lat is None or lon is None:
        return None

    city = detect_city_from_postal(postal_code)

    # distance Bruxelles
    dist_brussels = distance_to_brussels(lat, lon)

    # capitale la plus proche
    capital, dist_capital = nearest_capital(lat, lon, exclude_city=city)

    # RÈGLE: si déjà dans la capitale la plus proche → rien
    if city is not None and city == capital:
        return None

    return {
        "latitude": lat,
        "longitude": lon,
        "postal_code": postal_code,
        "city": city,
        "distance_brussels_km": dist_brussels,
        "nearest_capital": capital,
        "distance_nearest_capital_km": dist_capital
    }

result = analyze_property(url)
print(result)       
"""
        
    
def analyze_geo(lat, lon, postal_code):
    """
    Fonction propre que tu vas appeler depuis property_details_scraper
    """

    if lat is None or lon is None:
        return None

    city = detect_city_from_postal(postal_code)

    dist_brussels = distance_to_brussels(lat, lon)
    capital, dist_capital = nearest_capital(lat, lon, exclude_city=city)

    if city is not None and city == capital:
        return None

    return {
        "city": city,
        "distance_brussels_km": dist_brussels,
        "nearest_capital": capital,
        "distance_nearest_capital_km": dist_capital
    }