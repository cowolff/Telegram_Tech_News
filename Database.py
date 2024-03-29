import pathlib
import requests
import os
import sqlite3
import time
from datetime import datetime, timedelta

class Data:
    
    def __init__(self, filename="data.db"):

        #only checks whether the file exists if default path is used
        self.con = sqlite3.connect(filename)
        cur = self.con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS Users(userName TEXT, password TEXT, PRIMARY KEY(userName))''')
        cur.execute('''CREATE TABLE IF NOT EXISTS Chats(chatId INTEGER, PRIMARY KEY (chatId))''')
        cur.execute('''CREATE TABLE IF NOT EXISTS Settings(api_key TEXT, PRIMARY KEY (api_key))''')
        cur.execute('''CREATE TABLE IF NOT EXISTS RSS_News(title TEXT, tags TEXT, timestamp INT, link TEXT, relevance INT)''')
        cur.execute('''CREATE TABLE IF NOT EXISTS RSS_Feed(title TEXT, link TEXT, feedId INT, language TEXT, PRIMARY KEY(feedId))''')
        cur.execute('''CREATE TABLE IF NOT EXISTS RSS_Keyword(feedId INT, keyword TEXT)''')
        cur.execute('''CREATE TABLE IF NOT EXISTS RSS_Tag(feedId INT, tag TEXT)''')
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
        cur.execute('''CREATE TABLE IF NOT EXISTS Tipps(id INT, type STRING, foreignKey INT, timestamp INT)''')
        self.con.commit()
        cur.close()
        self.__initUser()
        self.__initIssueId()
        self.__initRSSId()
        self.__initTippsId()
        self.__initAPIKey()
        self.last_drop_asin = None

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
            self.RSSId = cur.fetchone()[0]
            cur.close()
        else:
            self.RSSId = 0

    def __initTippsId(self):
        cur = self.con.cursor()
        cur.execute('SELECT COUNT(*) FROM Tipps')
        result = cur.fetchone()[0]
        cur.close()
        if result != 0:
            cur = self.con.cursor()
            cur.execute('SELECT MAX(id) FROM Tipps')
            self.tippsId = cur.fetchone()[0]
            cur.close()
        else:
            self.tippsId = 0

    def __initAPIKey(self):
        cur = self.con.cursor()
        cur.execute("SELECT COUNT(*) FROM Settings")
        result = cur.fetchone()[0]
        cur.close()
        if result == 0:
            cur = self.con.cursor()
            cur.execute("INSERT INTO Settings VALUES('no_value')")
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
            self.con.commit()
            cur.close()
            return True
        except sqlite3.IntegrityError as e:
            print(e)
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
                self.last_drop_asin = asin
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

    def add_RSS_Feed(self, link, name, language):
        cur = self.con.cursor()
        self.RSSId = self.RSSId + 1
        cur.execute("INSERT INTO RSS_Feed VALUES('%s', '%s', %s, '%s');" % (name, link, self.RSSId, language))
        self.con.commit()
        cur.close()
        return self.RSSId

    def get_RSS_Feeds(self):
        cur = self.con.cursor()
        cur.execute("SELECT * FROM RSS_Feed")
        feeds = cur.fetchall()
        feeds = [{"title":x[0], "link":x[1], "feedId":x[2], "language":x[3]} for x in feeds]
        cur.close()
        return feeds

    def remove_RSS_Feed(self, link):
        cur = self.con.cursor()
        cur.execute("DELETE FROM RSS_Feed WHERE link='%s';" % link)
        self.con.commit()
        cur.close()

    def getDownloadNews(self):
        feeds = self.get_RSS_Feeds()
        result = []
        for feed in feeds:
            news = self.get_RSS_News(feed["link"], feed["title"])
            for new in news:
                current = {"title":new["title"], "tags":new["tags"], "source":feed["title"], "language":feed["language"], "timestamp":new["timestamp"], "relevance":new["relevance"]}
                result.append(current)
        return result

    def add_RSS_News(self, link, title, tags, timestamp, relevance):
        cur = self.con.cursor()
        try:
            print(title)
            cur.execute("INSERT INTO RSS_News VALUES('%s', '%s', '%s', '%s', '%s');" % (title, tags, int(round(timestamp)), link, relevance))
            self.con.commit()
            cur.close()
        except:
            cur.close()
            print("Couldnt add News with title: " + title + " and tags: " + tags)
 
    def get_RSS_News(self, link, name):
        cur = self.con.cursor()
        cur.execute("SELECT * FROM RSS_News WHERE link='%s' ORDER BY timestamp DESC;" % link)
        news = cur.fetchall()
        news = [{"title":x[0], "tags":x[1], "timestamp":x[2], "name":name, "relevance":x[4]} for x in news]
        cur.close()
        return news

    def get_RSS_Link_Title(self, id):
        cur = self.con.cursor()
        cur.execute("SELECT link, title FROM RSS_Feed WHERE feedId=%s;" % id)
        data = cur.fetchone()
        cur.close()
        return data[0], data[1]

    def add_news_tipp(self, foreign_id, type, timestamp):
        self.tippsId = self.tippsId + 1
        timestamp = int(round(float(timestamp)))
        cur = self.con.cursor()
        cur.execute("INSERT INTO Tipps VALUES('%s', '%s', '%s', '%s');" % (self.tippsId, type, foreign_id, timestamp))
        self.con.commit()
        cur.close()

    def get_news_tipps_by_id(self, id):
        cur = self.con.cursor()
        cur.execute("SELECT * FROM Tipps WHERE id='%s';" % (id))
        result = cur.fetchone()
        result = {"id":result[0], "type":result[1], "foreignKey":id, "timestamp":result[3]}
        cur.close()
        return result

    def get_news_number_by_timestamps(self, lower_range, upper_range):
        cur = self.con.cursor()
        cur.execute("SELECT Count(*) FROM RSS_News WHERE timestamp<%s AND timestamp>%s;" % (upper_range, lower_range))
        count = cur.fetchone()[0]
        cur.close()
        return count

    def get_RSS_Overview(self):
        overview = []
        feeds = self.get_RSS_Feeds()
        for feed in feeds:
            news = self.get_RSS_News(feed["link"], feed["title"])
            timestamp_today = time.time() - (24 * 60 * 60)
            number_relevant_news = len([x for x in news if x["relevance"]==1 and float(x["timestamp"]) > timestamp_today])
            number_relevant_news_total = len([x for x in news if x["relevance"]==1])
            number_news_total = len(news)
            try:
                latest_update = max([float(x["timestamp"]) for x in news])
                date = datetime.fromtimestamp(float(latest_update)).strftime("%d/%m/%Y, %H:%M:%S")
            except:
                date = "00.00.0000 00:00"
            overview.append({"feedId":feed["feedId"], "name":feed["title"], "language":feed["language"], "lastUpdate":date, "numberNews":number_news_total, "numberRelevantNews":number_relevant_news_total, "numberRelevantNewsToday":number_relevant_news})
        return overview

    def get_home(self):
        products = self.get_overview_products()
        if self.last_drop_asin is not None:
            prices = self.get_prices(self.last_drop_asin)
            prd_labels = [float(x[1]) for x in prices[0:20]]
            prd_prices = [float(x[0].replce(",",".").replace("€","")) for x in prices[0:20]]
        else:
            prd_labels = [0,0,0,0,0,0]
            prd_prices = [0,0,0,0,0,0]
        current_date = datetime.today()
        bar_counts = []
        bar_dates = []
        for i in range(7):
            upper_range = current_date.timestamp()
            current_date = current_date - timedelta(days=1)
            lower_range = current_date.timestamp()
            bar_counts.append(self.get_news_number_by_timestamps(lower_range, upper_range))
            bar_dates.append(current_date.timestamp())
        print(bar_dates)
        return products, prd_labels, prd_prices, bar_counts, bar_dates
        
    def add_rss_keyword(self, feedId, keyword):
        cur = self.con.cursor()
        cur.execute("INSERT INTO RSS_Keyword VALUES('%s', '%s')" % (feedId, keyword))
        self.con.commit()
        cur.close()

    def get_rss_keywords(self, feedId):
        cur = self.con.cursor()
        cur.execute("SELECT keyword FROM RSS_Keyword WHERE feedId='%s'" % (feedId))
        keywords = [{"word":str(x[0]).lower()} for x in cur.fetchall()]
        cur.close()
        return keywords

    def remove_rss_keyword(self, feedId, keyword):
        cur = self.con.cursor()
        cur.execute("DELETE FROM RSS_Keyword WHERE keyword='%s' AND feedId='%s'" % (keyword, feedId))
        self.con.commit()
        cur.close()

    def remove_rss_tag(self, feedId, tag):
        cur = self.con.cursor()
        cur.execute("DELETE FROM RSS_Tag WHERE tag='%s' AND feedId='%s'" % (tag, feedId))
        self.con.commit()
        cur.close()

    def add_rss_tag(self, feedId, tag):
        cur = self.con.cursor()
        cur.execute("INSERT INTO RSS_Tag VALUES('%s', '%s')" % (feedId, tag))
        self.con.commit()
        cur.close()

    def get_rss_tags(self, feedId):
        cur = self.con.cursor()
        cur.execute("SELECT tag FROM RSS_Tag WHERE feedId='%s'" % (feedId))
        tags = [{"tag":str(x[0]).lower()} for x in cur.fetchall()]
        cur.close()
        return tags

    def update_priority(self, title, tags, priority):
        cur = self.con.cursor()
        cur.execute("UPDATE RSS_News SET priority=%s WHERE title='%s' AND tags='%s'" % (priority, title, tags))
        self.con.commit()
        cur.close()

    def get_api_key(self):
        cur = self.con.cursor()
        cur.execute("SELECT * FROM Settings")
        api_key = {"api_key": cur.fetchone()[0]}
        cur.close()
        return api_key

    def update_api_key(self, new_key):
        cur = self.con.cursor()
        cur.execute("UPDATE Settings SET api_key='%s'" % (new_key))
        self.con.commit()
        cur.close()
