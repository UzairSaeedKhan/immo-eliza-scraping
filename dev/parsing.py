
import requests, re
from bs4 import BeautifulSoup

url = "https://immovlan.be/en/detail/duplex/for-sale/1000/brussels/vbe35095"
html = requests.get(url, headers={"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"}).text

#def scrape_features(url):
soup = BeautifulSoup(html, "html.parser")


def text_of(tag):
#Return stripped text of a tag, or None if the tag wasn't found.
#Avoids 'NoneType has no attribute get_text' crashes."""
   return tag.get_text(strip=True) if tag else None
def value_after_h4(label):
    h4 = soup.find("h4", string=lambda x: x and label.lower() in x.lower())
    if not h4:
        return None
    block = h4.find_parent()

    # récupère tous les textes du bloc
    texts = block.stripped_strings

    # saute le label, garde la valeur
    next(texts, None)
    value = next(texts, None)

    return value
    #h4 = soup.find("h4", string=label)

    #return text_of(h4.find_next("p")) if h4 else None
#def binary_element(label):

    #blocks = soup.find_all("div")

    #value = value_after_h4(label)

    #if value in ["yes", "true"]:
     #   return 1
    #elif value in ["no", "false"]:
     #   return 0
    #else:
     #   return None

    #return None

def binary_element(label):

    label = label.lower()

    for tag in soup.find_all(string=True):

        if tag and label in tag.lower():

            parent_text = tag.parent.get_text(" ", strip=True).lower()

            if "yes" in parent_text:
                return 1
            if "no" in parent_text:
                return 0

    return None
price_raw = soup.find("span", class_="detail__header_price_data")


if price_raw:
    price = price_raw.get_text(strip=True)
    price = price.replace("\u202f", " ")
else:
    price = None
Tags = {
#list of caracteristics
    "price_tag" : price,
    #"property_id_tag" : text_of(soup.find("span", class_="vlancode")),
    #"postal_code_tag" : text_of(soup.find("span", class_="city-line")),
# use a CSS selector so multi-class elements match regardless of class order
    "livable_surface_tag" : value_after_h4("Surface"),
    "construction_year_tag" : value_after_h4("Build Year"),
    "number_of_bedrooms" : value_after_h4("Number of bedrooms"),
    "number_of_bathrooms" : value_after_h4("Number of bathrooms"),
    "number_of_toilets" : value_after_h4("Number of toilets"),
    "VAT_included" : binary_element("VAT"),
    "terrace_included" : binary_element("Terrace"),
    "Elevator_included" : binary_element("Ascenseur"),
    "Garden" : value_after_h4("Garden")
}
print(Tags)
  


