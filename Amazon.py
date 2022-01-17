import requests #pip install requests
from bs4 import BeautifulSoup #pip install bs4
import os
import time
import json
import random
from Database import Data
from Update import send_message, send_message_to_chats
from datetime import datetime, timedelta
import threading

# Google "My User Agent" And Replace It

headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'} 
process = "Amazon Crawler"
file = "Amazon.py"

def amazon_process(api_key):
    while True:
        data = Data()
        chat_ids = data.get_chats()
        minute = random.randrange(0, 59)
        second = random.randrange(0, 59)
        x=datetime.today()
        y = x.replace(day=x.day, hour=7, minute=minute, second=second, microsecond=0) + timedelta(days=1)
        delta_t=y-x
        secs=delta_t.total_seconds()
        time.sleep(secs)
        thread = threading.Thread(target=start, daemon=True, args=(api_key, chat_ids))
        thread.start()

def __check_single_price_error(asin, error, lines, data):
    description = str(error)
    line = lines
    severity = 3
    price = data.get_last_price(asin)
    data.add_Issue(process, description, file, line, severity)
    dic = {"asin":asin, "title":"null", "price":str(price)}
    print("Error in check_single_price: " + str(error))
    return dic

def __check_search_error(term, error, lines, data):
    description = str(error)
    line = lines
    severity = 3
    data.add_Issue(process, description, file, line, severity)
    print("Error in check_search: " + str(error))

#Checking the price
def check_single_price(ASIN, data):
    try:
        URL = "https://www.amazon.de/dp/" + ASIN + "/"
        page = requests.get(URL, headers=headers)
        soup  = BeautifulSoup(page.content, 'html.parser')

        #Finding the elements
        product_title = soup.find(id='productTitle').text

        if soup.find(id='corePrice_desktop') is not None:
            try:
                product_price = soup.find(id='corePrice_desktop')
                product_price = product_price.findAll("span", {"class", "a-price a-text-price a-size-medium apexPriceToPay"})[0]
                product_price = product_price.findAll("span", {"class", "a-offscreen"})[0].text
            except IndexError:
                print("couldn't find price for " + URL)
                product_price = "-1,0€"

        elif len(soup.findAll("span", {"class":"a-price-whole"})) != 0:
            try:
                product_price = soup.findAll("span", {"class":"a-price-whole"})[0].text
                product_price = product_price + soup.findAll("span", {"class":"a-price-fraction"})[0].text + "€"
            except IndexError:
                print("couldn't find price for " + URL)
                product_price = "-1,0€"

        else:
            print("Couldn't get price at " + ASIN)
            product_price = -1
        dic = {"asin":ASIN, "title":product_title.replace("  ", ""), "price":product_price}
        return dic
        
    except Exception as e:
        return __check_single_price_error(ASIN, e, "29-54", data)
        

def check_search(TERM, data):
    products = []
    try:
        TERM = TERM.replace(" ", "+")
        URL = "https://www.amazon.de/s?k=" + TERM

        page = requests.get(URL, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')

        product_list = soup.findAll("div", {"class":"s-main-slot s-result-list s-search-results sg-row"})[0]
        product_list = product_list.findAll("div", {"class":"s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col s-widget-spacing-small sg-col-12-of-16"})

        for product in product_list:
            try:
                asin = product["data-asin"]
                title = product.findAll("h2", {"class":"a-size-mini a-spacing-none a-color-base s-line-clamp-2"})[0].text
                try:
                    price = str(product.findAll("span", {"class":"a-price-whole"})[0].text) + "€"
                except IndexError:
                    print("couldn't find price for https://www.amazon.de/dp/" + asin)
                    price = "-1,0€"
                dic = {"asin":asin, "title": title, "price": price}
                products.append(dic)
            except Exception as e:
                __check_search_error(TERM, e, "82-90", data)
        return products
    except Exception as e:
        __check_search_error(TERM, e, "70-93", data)
        return products

def start(api_key, chat_ids):

    data = Data()
    
    print("Start searching")
    search_terms = data.get_amazon_search_terms()
    # search_terms = ["Galaxy S","8 GB RAM"]
    asins = []
    for term in search_terms:
        time.sleep(random.uniform(0,30))
        timestamp = time.time()
        products = check_search(term, data)
        for product in products:
            asins.append(product["asin"])
            if not data.product_exists(product["asin"]):
                data.add_amazon_product(product["title"], product["asin"])
            data.add_amazon_search_instance(term, timestamp)
            data.add_amazon_search_result(term, timestamp, product["asin"])
            data.add_amazon_price(product["asin"], product["price"], timestamp)
            if(data.check_drop(product["asin"], 0.1)):
                send_message_to_chats("Das Produkt \n\n" + product["title"] + "\nmit dem Link: https://www.amazon.de/dp/" + product["asin"] + "/\n\nist signifikant im Preis gefallen"
                                + "\n\n das Produkt wurde im Rahmen des Surch-Terms '" + term + "' aufgezeichnet", data.get_chats(), api_key, 0, "Amazon - " + product["asin"])

    watchlist = data.get_watchlist()
    # watchlist = [["B08ZLW675G"],["B07CMH5F9R"],["B081QX9V2Y"],["B08CVJ59G3"], ["B09L61QRM1"]]

    watchlist = [e for e in watchlist if e not in asins]
    print("Watchlist:", watchlist)
    for element in watchlist:
        timetamp = time.time()
        result = check_single_price(element, data)
        data.add_amazon_price(result["asin"], result["price"], timetamp)
        if(data.check_drop(result["asin"], 0.1)):
            send_message_to_chats("Das Produkt \n\n" + result["title"] + "\nmit dem Link: https://www.amazon.de/dp/" + result["asin"] + "/\n\nist signifikant im Preis gefallen",  data.get_chats(), api_key, 0, "Amazib - " + result["asin"])
        time.sleep(random.uniform(0,30))




api = "1719127362:AAHSCLN1M5BoGg3pt3AUYz0MH7W8uPvIcfY"
chat_ids = ["653734838"]

# start(data, api, chat_ids)

# check_search("Galaxy A")