import requests, re
from bs4 import BeautifulSoup

url = "https://immovlan.be/en/detail/apartment/for-sale/2390/oostmalle/rbw20430"

#Global function contains all the functions related to scraping data
def scrape_features(url):

    html = requests.get(url, headers={"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"}).text


    soup = BeautifulSoup(html, "html.parser")


    #Take the value after h4 in the HTML file (the <p> block)    
    def value_after_h4(label):
        h4 = soup.find("h4", string=lambda x: x and label.lower() in x.lower())
        if not h4:
            return None
        block = h4.find_parent()

        # retrieves all the text in the block
        texts = block.stripped_strings

        # only keeps the value
        next(texts, None)
        value = next(texts, None)

        return value


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

        return "0"


    #EPC score storing
    meta_desc = soup.find("meta", attrs={"name": "description"})

    epc = None

    if meta_desc:
        description = meta_desc.get("content", "")

        match = re.search(r"EPC\s+([A-G]\+?)", description)

        if match:
            epc = match.group(1)


    #To store and clean the price
    price_raw = soup.find("span", class_="detail__header_price_data")

    if price_raw:
        price = price_raw.get_text(strip=True)
        price = price.replace("\u202f", " ")
    else:
        price = None


    #Train station distance storing
    def get_train_distance(mode):
        blocks = soup.find_all("div", class_="data-row")

        for block in blocks:

            h3 = block.find("h3")

            if not h3:
                continue

            if "Train stations" not in h3.get_text(" ", strip=True):
                continue

            spans = block.find_all("span", title=mode)

            if spans:
                # on prend le premier span du bloc Train stations
                return spans[0].get_text(" ", strip=True)

        return None
    
    #Property id
    property_id = soup.find("span", class_ = "vlancode").get_text(strip=True)

    #Results
    Tags = {
        "property_id" : property_id,
        "price" : price,
        "vat_included" : binary_element("VAT"),
        
        "state_of_property" : value_after_h4("State of property"),
        "livable_surface" : value_after_h4("Surface"),
        "construction_year" : value_after_h4("Build Year"),
        "epc_score" : epc,
        
        "nb_of_facades" : value_after_h4("Number of facades"),
        "nb_of_floors" : value_after_h4("Number of floors"),
        "nb_of_bedrooms" : value_after_h4("Number of bedrooms"),
        "nb_of_bathrooms" : value_after_h4("Number of bathrooms"),
        "nb_of_showers" : value_after_h4("Number of showers"),
        "nb_of_toilets" : value_after_h4("Number of toilets"),
        
        "terrace" : binary_element("Terrace"),
        "elevator" : binary_element("Elevator"),
        "access_for_disabled" : binary_element("Access for disabled"),
        "garden" : binary_element("Garden"),
        "garage" : binary_element("Garage"), 
        "swimming_pool" : binary_element("Swimming pool"), 
        
        "distance_from_train_stations_by_foot": get_train_distance("Walking"),
        "distance_from_train_stations_by_car": get_train_distance("Driving")}
    

    for key, value in Tags.items():
        print(f"- {key}: {value}")

scrape_features(url)