import requests
from bs4 import BeautifulSoup
from Database import Data
from Update import send_message
import time

def build_url(URL, country):
    if country == "DE":
        return "https://www.amazon.de/gp/product/" + URL

def get_price(URL, country):
    url = build_url(URL, country)
    headers = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0"
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(id)
    title = soup.find(id="productTitle")
    price = soup.find(id="priceblock_dealprice")
    if price is None:
        price = soup.find(id="priceblock_ourprice")
    elif price is None:
        price = -1

    return price, title

def check_deals(database: Data, api_key):
    devices = database.get_all_products()
    for device in devices:
        url = device[3]
        country = device[4]
        price, title = get_price(url, country)
        database.add_amazon_price(title, price)

        prices = database.get_prices(title, country)

        if prices[-1] / prices[-2] < 0.9:
            chat_ids = database.get_chats()
            for chat in chat_ids:
                send_message(f"Das Produkt {title} ist um {str(1 - (price[-1] / price[-2]))} im Preis gefallen.", chat, api_key)

def product_in_database(URL, country, manufacturer, database: Data):
    price, title = get_price(URL, country)
    if not database.product_exists(title, country):
        database.add_amazon_product(title, manufacturer, country, URL)
        database.add_amazon_price(title, price)

def load_config(path):
    config = open(path)
    # TO-DO: Config file laden

def check_loop(api_key: str, database: Data):
    load_config()
    while True:
        check_deals(database, api_key)
        time.sleep(60 * 60 * 24)