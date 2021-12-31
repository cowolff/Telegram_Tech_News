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
        cur.execute('''CREATE TABLE IF NOT EXISTS RSS_News(title TEXT, content TEXT, timestamp TEXT, link TEXT, relevance INT)''')
        cur.execute('''CREATE TABLE IF NOT EXISTS RSS_Feed(title TEXT, link TEXT, feedId INT, PRIMARY KEY(feedId))''')
        cur.execute('''CREATE TABLE IF NOT EXISTS Amazon_Product(title TEXT, asin TEXT, PRIMARY KEY(asin))''')
        cur.execute('''CREATE TABLE IF NOT EXISTS Amazon_Search_Term(term TEXT, PRIMARY KEY(term))''')
        cur.execute('''CREATE TABLE IF NOT EXISTS Amazon_Search_Instance(term TEXT, timestamp TEXT, FOREIGN KEY(term) REFERENCES Amazon_Search_Term(term))''')
        cur.execute('''CREATE TABLE IF NOT EXISTS Amazon_Search_Result(term TEXT, timestamp TEXT, asin TEXT, FOREIGN KEY(term) REFERENCES Amazon_Search_Term(term))''')
        cur.execute('''CREATE TABLE IF NOT EXISTS Amazon_Price
                    (asin TEXT, timestamp INTEGER, price TEXT, 
                    FOREIGN KEY(asin) REFERENCES Amazon_Product(asin))''')
        cur.execute('''CREATE TABLE IF NOT EXISTS Amazon_Watchlist
                    (asin TEXT, PRIMARY KEY(asin))''')
        cur.execute('''CREATE TABLE IF NOT EXISTS Issues(id INT, process TEXT, description TEXT, file TEXT, line TEXT, timestamp TEXT, severity INT, done TEXT, PRIMARY KEY(id))''')
        self.con.commit()
        cur.close()
        self.__initUser()
        self.__initIssueId()
        self.__initRSSId()

    def __initUser(self):
        cur = self.con.cursor()
        cur.execute('SELECT COUNT(*) FROM Users')
        result = cur.fetchone()[0]
        if result == 0:
            cur.execute("INSERT INTO Users VALUES('cowolff','1234567')")
            self.con.commit()
        cur.close()

    def __initIssueId(self):
        cur = self.con.cursor()
        cur.execute('SELECT COUNT(*) FROM Issues')
        result = cur.fetchone()[0]
        cur.close()
        if result != 0:
            cur = self.con.cursor()
            cur.execute('SELECT MAX(id) FROM Issues')
            self.id = cur.fetchone()[0]
            cur.close()
        else:
            self.id = 0

    def __initRSSId(self):
        cur = self.con.cursor()
        cur.execute('SELECT COUNT(*) FROM RSS_Feed')
        result = cur.fetchone()[0]
        cur.close()
        if result != 0:
            cur = self.con.cursor()
            cur.execute('SELECT MAX(feedId) FROM RSS_Feed')
            self.RSSid = cur.fetchone()[0]
            cur.close()
        else:
            self.RSSid = 0


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

    def add_amazon_product(self, title, asin):
        cur = self.con.cursor()
        cur.execute("INSERT INTO Amazon_Product VALUES('" + title + "','" +  asin + "')")
        self.con.commit()
        cur.close()

    def product_exists(self, asin):
        cur = self.con.cursor()
        try:
            cur.execute("SELECT Count(*) FROM Amazon_Product WHERE asin='%s'" % (asin))
            n = cur.fetchone()[0]
            if n == 0:
                return False
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
    
    def get_last_price(self, asin):
        prices = self.get_prices(asin)
        if len(prices) == 0:
            return 0
        else:
            return prices[0][0]

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
        asins = [x[0] for x in asins]
        cur.close()
        return asins

    def add_amazon_watchlist(self, asin):
        try:
            cur = self.con.cursor()
            cur.execute("INSERT INTO Amazon_Watchlist VALUES('%s');" % asin)
            cur.close()
            return True
        except sqlite3.IntegrityError:
            cur.close()
            return False

    def remove_amazon_watchlist(self, asin):
        try:
            cur = self.con.cursor()
            cur.execute("DELETE FROM Amazon_Watchlist WHERE asin = '%s';" % asin)
            cur.close()
            return True
        except sqlite3.error:
            cur.close()
            return False


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
        if(len(prices) > 1 and prices[0][0] != "-1,0€" and prices[0][1] != "-1,0€"):
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

    def add_Issue(self, process, description, file, line, severity):
        timestamp = str(time.time())
        done = "False"
        cur = self.con.cursor()
        self.id = self.id + 1
        cur.execute("INSERT INTO Issues VALUES(%s, '%s', '%s', '%s', '%s', '%s', %s, '%s')" % (self.id, process, description, file, line, timestamp, severity, done))
        self.con.commit()
        cur.close()

    def done_Issue(self, update_id, done):
        cur = self.con.cursor()
        cur.execute("UPDATE Issues SET done='%s' WHERE id='%s';" % (update_id, done))
        self.con.commit()
        cur.close()

    def get_Issues(self):
        cur = self.con.cursor()
        cur.execute("SELECT * FROM Issues;")
        issues = cur.fetchall()
        dict = []
        for issue in issues:
            date = datetime.fromtimestamp(float(issue[5])).strftime("%d/%m/%Y, %H:%M:%S")
            dic = {"id":issue[0], "process":issue[1], "description":issue[2], "file":issue[3], "line":issue[4], "timestamp":date, "severity":issue[6], "done":issue[7]}
            dict.append(dic)
        return dict

    def get_Term_Overview(self):
        cur = self.con.cursor()
        asins = self.get_watchlist()
        overview = []
        cur.execute("SELECT * FROM Amazon_Search_Term")
        terms = cur.fetchall()
        cur.close()
        terms = [term[0] for term in terms]
        for term in terms:
            try:
                cur = self.con.cursor()
                cur.execute("SELECT timestamp FROM Amazon_Search_Instance WHERE term='%s'" % (term))
                timestamp = cur.fetchone()[0]
                date = datetime.fromtimestamp(float(timestamp)).strftime("%d/%m/%Y, %H:%M:%S")
                cur.close()
                cur = self.con.cursor()
                cur.execute("SELECT * FROM Amazon_Search_result WHERE term='%s' AND timestamp='%s'" % (term, timestamp))
                results = cur.fetchall()
                numberOfProducts = len(results)
                trackedAsins = [x[2] for x in results]
                numberOfTrackedProducts = len([x for x in trackedAsins if x in asins])
                cur.close()
                dic = {"term":term, "numberProducts":str(numberOfProducts), "singleProducts":str(numberOfTrackedProducts), "lastUpdate":date}
                overview.append(dic)
            except Exception as e:
                print(e)
                dic = {"term":term, "numberProducts":"-1", "singleProducts":"-1", "lastUpdate":"0.0.0000 00:00:00"}
                overview.append(dic)
        return overview

    def add_RSS_Feed(self, link, name):
        cur = self.con.cursor()
        self.RSSid = self.RSSid + 1
        cur.execute("INSERT INTO RSS_Feed VALUES('%s', '%s', %s)" % (link, name, self.RSSid))
        self.con.commit()
        cur.close()

    def get_RSS_Feeds(self):
        cur = self.con.cursor()
        cur.execute("SELECT * FROM RSS_Feed")
        feeds = cur.fetchall()
        feeds = [{"title":x[0], "link":x[1], "feedId":x[2]} for x in feeds]
        cur.close()
        return feeds

    def remove_RSS_Feed(self, link):
        cur = self.con.cursor()
        cur.execute("DELETE FROM RSS_Feed WHERE link='%s';" % link)
        self.con.commit()
        cur.close()

    def add_RSS_News(self, link, title, content, timestamp, relevance):
        cur = self.con.cursor()
        cur.execute("INSERT INTO RSS_News VALUES('%s','%s','%s','%s', %s);" % (title, content, str(timestamp), link, relevance))
        self.con.commit()
        cur.close()

    def get_RSS_News(self, link, name):
        cur = self.con.cursor()
        cur.execute("SELECT * FROM RSS_News WHERE link='%s';" % link)
        news = cur.fetchall()
        news = [{"title":x[0], "content":[1], "timestamp":x[2], "name":name, "relevance":x[4]} for x in news]
        cur.close()
        return news

    def get_RSS_Link_Title(self, id):
        cur = self.con.cursor()
        cur.execute("SELECT link, title FROM RSS_Feed WHERE feedId=%s;" % id)
        data = cur.fetchone()
        cur.close()
        return data[0], data[1]