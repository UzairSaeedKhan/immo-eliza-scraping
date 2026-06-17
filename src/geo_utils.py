#DISTANCE API

    def get_postal_code():
        city = soup.find("span", class_="city-line")

        if not city:
            return None

        digits = "".join(c for c in city.get_text() if c.isdigit())

        if len(digits) == 4:
            return int(digits)

        return None
    postal_code = get_postal_code()

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

      "distance_to_brussels_in_km_by_car": get_distance_to_brussels(soup, lon, postal_code),
        "nearest_capital": nearest_city,
        "distance_to_nearest_capital_km": distance,