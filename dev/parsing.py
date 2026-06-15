
import requests
from bs4 import BeautifulSoup

url = "https://immovlan.be/fr/detail/appartement/a-louer/1348/louvain-la-neuve/vwd17760"
html = requests.get(url, headers={"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"}).text

#def scrape_features(url):
soup = BeautifulSoup(html, "html.parser")

Tags = {
        #list of caracteristics
    "price_tag" :  soup.find("span", class_="detail__header_price_data").get_text(strip=True),
    "property_id_tag" : soup.find("span", class_="vlancode").get_text(strip=True),
    "postal_code_tag" : soup.find("span", class_="city-line").get_text(strip=True),
    "livable_surface_tag" : soup.find("span", class_="property-highlight margin-bottom-05 margin-right-05").get_text(strip=True),
    "construction_year_tag" : ("h4", {"Build Year"}).get_text(strip=True)
    }
print(Tags)
    #price_tag = None
    #if price_tag:
      #  price = price.text.strip().split("-")[0].replace("€", "").replace(" ", "")
     #   price = int(price)
    #for key, (tag, class_name) in selectors.items():
    #element = soup.find(tag, class_=class_name)
    #characteristics[key] = element.get_text(strip=True) if element else None

    #property_id = id_tag.text.strip() 
    #if id_tag 
    #else None

    #return {
     #   "property_id": property_id,
      #  "price": price
    #}

    #if not tag:
     #   return None
    
    #else:
     #   return {
      #      "property_id": parse_property_id(soup),
       #     "price": price,
        #    "bedrooms": ...,
    #}

