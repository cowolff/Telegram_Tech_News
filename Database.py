import pathlib
import requests
import os
import sqlite3
import time
from datetime import datetime

class Data:
    
    def __init__(self, filename="data.db"):

        #only checks whether the file exists if default path is used
        self.con = sqlite3.connect(filename)
        cur = self.con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS Users(userName TEXT, password TEXT, PRIMARY KEY(userName))''')
        cur.execute('''CREATE TABLE IF NOT EXISTS Chats(chatId INTEGER, PRIMARY KEY (chatId))''')
        cur.execute('''CREATE TABLE IF NOT EXISTS Settings(api_key TEXT, PRIMARY KEY (api_key))''')
        cur.execute('''CREATE TABLE IF NOT EXISTS RSS_News(title TEXT, timestamp TEXT)''')
        cur.execute('''CREATE TABLE IF NOT EXISTS Amazon_Product(title TEXT, asin TEXT, PRIMARY KEY(asin))''')
        cur.execute('''CREATE TABLE IF NOT EXISTS Amazon_Search_Term(term TEXT, PRIMARY KEY(term))''')
        cur.execute('''CREATE TABLE IF NOT EXISTS Amazon_Search_Instance(term TEXT, timestamp TEXT, FOREIGN KEY(term) REFERENCES Amazon_Search_Term(term))''')
        cur.execute('''CREATE TABLE IF NOT EXISTS Amazon_Search_Result(term TEXT, timestamp TEXT, asin TEXT, FOREIGN KEY(term) REFERENCES Amazon_Search_Term(term))''')
        cur.execute('''CREATE TABLE IF NOT EXISTS Amazon_Price
                    (asin TEXT, timestamp INTEGER, price TEXT, 
                    FOREIGN KEY(asin) REFERENCES Amazon_Product(asin))''')
        cur.execute('''CREATE TABLE IF NOT EXISTS Amazon_Watchlist
                    (asin TEXT, PRIMARY KEY(asin))''')
        self.con.commit()
        cur.close()
        self.__initUser()

    def __initUser(self):
        cur = self.con.cursor()
        cur.execute('SELECT COUNT() FROM Users')
        result = cur.fetchone()[0]
        if result == 0:
            cur.execute("INSERT INTO Users VALUES('cowolff','1234567')")
            self.con.commit()
        cur.close()

    def create_user(self, username, password):
        cur = self.con.cursor()
        cur.execute('INSERT INTO Users VALUES(' + username + ',' + password + ')')
        self.con.commit()
        cur.close()

    def check_password(self, username, password):
        cur = self.con.cursor()
        cur.execute("SELECT password FROM Users WHERE userName='" + username + "'")
        try:
            correct_password = cur.fetchone()[0]
            if password == correct_password:
                return True
            else:
                return False
        except (sqlite3.OperationalError, TypeError):
            return False

    def update_password(self, username, old_password, new_password):
        if not self.check_password(username, old_password):
            return False
        cur = self.con.cursor()
        cur.execute("UPDATE Users SET password=" + new_password + " WHERE userName='" + username + "'")
        self.con.commit()
        cur.close()

    def get_chats(self):
        cur = self.con.cursor()
        cur.execute('''SELECT * FROM Chats''')
        users = [x[0] for x in cur.fetchall()]
        cur.close()
        return users

    def add_chats(self, chat_ids):
        cur = self.con.cursor()
        for id in chat_ids:
            cur.execute('''INSERT INTO Chats VALUES (''' + str(id) + ')')
        self.con.commit()
        cur.close()

    def remove_chats(self, chat_ids):
        cur = self.con.cursor()
        for id in chat_ids:
            cur.execute('''DELETE FROM Chats WHERE chatId=''' + str(id))
        self.con.commit()
        cur.close()

    def get_rss_news(self):
        cur = self.con.cursor()
        cur.execute('SELECT title FROM RSS_News')
        news = [x[0] for x in cur.fetchall()]
        cur.close()
        return news

    def add_rss_news(self, title):
        timestamp = time.time()
        cur = self.con.cursor()
        cur.execute("INSERT INTO RSS_News VALUES('" + title + "','" + str(timestamp) + "')")
        self.con.commit()
        cur.close()

    def add_amazon_product(self, title, asin):
        cur = self.con.cursor()
        cur.execute("INSERT INTO Amazon_Product VALUES('" + title + "','" +  asin + "')")
        self.con.commit()
        cur.close()

    def product_exists(self, asin):
        cur = self.con.cursor()
        try:
            cur.execute("SELECT Count() FROM Amazon_Product WHERE asin='%s'" % (asin))
            n = cur.fetchone()[0]
            return True
        except sqlite3.OperationalError as e:
            return False

    def get_products(self):
        cur = self.con.cursor()
        cur.execute("SELECT * FROM Amazon_Product")
        products = cur.fetchall()
        cur.close()
        return products

    def add_amazon_price(self, asin, price, timestamp):
        cur = self.con.cursor()
        cur.execute("INSERT INTO Amazon_Price VALUES('" + asin + "'," + str(timestamp) + ",'" + str(price) + "')")
        self.con.commit()
        cur.close()

    def get_prices(self, asin):
        cur = self.con.cursor()
        cur.execute("""SELECT price, timestamp from Amazon_Price WHERE asin="%s" ORDER BY timestamp DESC;""" % (asin))
        prices = cur.fetchall()
        cur.close()
        return prices
    
    def get_last_price(self, title, country):
        return self.get_prices(title, country)[0]

    def get_all_products(self):
        cur = self.con.cursor()
        cur.execute("SELECT title, product, country FROM Amazon_Product")
        all_products = cur.fetchall()
        cur.close()
        return all_products

    def get_products_by_manufacturer(self, manufacturer):
        cur = self.con.cursor()
        cur.execute("SELECT title, country FROM Amazon_Product WHERE manufacturer=%s;" % manufacturer)
        products = cur.fetchall()
        cur.close()
        return products

    def get_watchlist(self):
        cur = self.con.cursor()
        cur.execute("SELECT * FROM Amazon_Watchlist")
        asins = cur.fetchall()
        cur.close()
        return asins

    def get_product(self, asin):
        cur = self.con.cursor()
        cur.execute("""SELECT * FROM Amazon_Product WHERE asin="%s";""" % asin)
        product = cur.fetchone()[0]
        title = product[0]
        asin = product[3]
        dic = {"asin":asin, "title":title}
        return dic

    def check_drop(self, asin, threshold):
        prices = self.get_prices(asin)
        if(len(prices) > 1):
            first = prices[0][0].split(",")[0]
            second = prices[1][0].split(",")[0]
            if((float(first) / float(second)) < (1 - threshold)):
                return True
            else:
                return False
        else:
            return False

    def add_amazon_search_term(self, term):
        cur = self.con.cursor()
        cur.execute("INSERT INTO Amazon_Search_Term VALUES('" + term + "')")
        self.con.commit()
        cur.close()

    def get_amazon_search_terms(self):
        cur = self.con.cursor()
        cur.execute("SELECT * FROM Amazon_Search_Term")
        terms = cur.fetchall()
        terms = [term[0] for term in terms]
        cur.close()
        return terms

    def remove_amazon_search_term(self, term):
        cur = self.con.cursor()
        cur.execute("DELETE FROM Amazon_Search_Term WHERE term='" + term + "'")
        self.con.commit()
        cur.close()

    def add_amazon_search_instance(self, term, timestamp):
        cur = self.con.cursor()
        cur.execute("INSERT INTO Amazon_Search_Instance VALUES('" + term + "', '" + str(timestamp) + "')")
        self.con.commit()
        cur.close()

    def get_amazon_search_instances(self, term):
        cur = self.con.cursor()
        cur.execute("SELECT * FROM Amazon_Search_Instance WHERE term='" + term + "'")
        instances = cur.fetchall()
        cur.close()
        return instances

    def add_amazon_search_result(self, term, timestamp, asin):
        cur = self.con.cursor()
        cur.execute("INSERT INTO Amazon_Search_Result VALUES('" + term + "', '" + str(timestamp) + "', '" + asin + "')")
        self.con.commit()
        cur.close()

    def get_amazon_search_results(self, term, asin):
        cur = self.con.cursor()
        cur.execute("SELECT * FROM Amazon_Search_Result WHERE term='" + term + "' AND asin='" + asin + "'")
        results = cur.fetchall()
        cur.close()
        return results

    def get_overview_products(self):
        products = self.get_products()
        overview = []
        for product in products:
            prices = self.get_prices(product[1])
            price = prices[0][0]
            if len(prices) > 1:
                first_price = float(prices[1][0].replace("€","").replace(",",".").replace(".",""))
                second_price = float(prices[0][0].replace("€","").replace(",",".").replace(".",""))
                change = str(1-(second_price / first_price)) + "%"
            else:
                change = "0%"
            timestamp = prices[0][1]
            date = datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y, %H:%M:%S")
            dic = {"name":product[0], "asin":product[1], "lastUpdate":date, "price":price, "change":change}
            overview.append(dic)
        return overview
