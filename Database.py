import pathlib
import requests
import os
import sqlite3
import time

class Data:
    
    def __init__(self, filename="settings/chats.db"):

        #only checks whether the file exists if default path is used
        self.con = sqlite3.connect(filename)
        cur = self.con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS Users(userId INT PRIMARY KEY)''')
        cur.execute('''CREATE TABLE IF NOT EXISTS RSS_News(title TEXT PRIMARY KEY, timestamp TEXT)''')
        cur.execute('''CREATE TABLE IF NOT EXISTS Amazon_Product
                    (title TEXT, manufacturer TEXT, country TEXT, url TEXT,
                    PRIMARY KEY(title))''')
        cur.execute('''CREATE TABLE IF NOT EXISTS Amazon_Price
                    (title TEXT, timestamp INTEGER, price TEXT, 
                    FOREIGN KEY(title) REFERENCES Amazon_Product(title))''')
        self.con.commit()
        cur.close()

    def get_chats(self):
        cur = self.con.cursor()
        cur.execute('''SELECT * FROM Users''')
        users = [x[0] for x in cur.fetchall()]
        cur.close()
        return users

    def add_chats(self, chat_ids):
        cur = self.con.cursor()
        for id in chat_ids:
            cur.execute('''INSERT INTO Users VALUES (''' + str(id) + ')')
        self.con.commit()
        cur.close()

    def remove_chats(self, chat_ids):
        cur = self.con.cursor()
        for id in chat_ids:
            cur.execute('''DELETE FROM Users WHERE userId=''' + str(id))
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

    def add_amazon_product(self, title, manufacturer, country, url):
        cur = self.con.cursor()
        cur.execute("INSERT INTO Amazon_Product VALUES('" + title + "','" + manufacturer + "','" + country + "','" + url + "')")
        self.con.commit()
        cur.close()

    def product_exists(self, title, country):
        cur = self.con.cursor()
        cur.execute("SELECT Count() FROM Amazon_Product WHERE title=%s AND country=%s" % (title, country))
        n = cur.fetchone()[0]
        if n == 0:
            return False
        else:
            return True

    def get_products(self):
        cur = self.con.cursor()
        cur.execute("SELECT * FROM Amazon_Product")
        products = cur.fetchall()
        cur.close()
        return products

    def add_amazon_price(self, title, price):
        timetamp = time.time()
        cur = self.con.cursor()
        cur.execute("INSERT INTO Amazon_Price VALUES('" + title + "'," + timetamp + ",'" + price + "')")
        self.con.commit()
        cur.close()

    def get_prices(self, title, country):
        cur = self.con.cursor()
        cur.execute("SELECT price from Amazon_Price WHERE title=%s AND country=%s ORDER BY timestamp DESC;" % (title, country))
        prices = [x[0] for x in cur.fetchall()]
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