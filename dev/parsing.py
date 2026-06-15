
import requests
from bs4 import BeautifulSoup

url = "https://immovlan.be/fr/projectdetail/1507364-157"


html = requests.get(url, headers={"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"}).text

soup = BeautifulSoup(html, "html.parser")

html.find(span class="detail__header_price_data")

print(html.find)