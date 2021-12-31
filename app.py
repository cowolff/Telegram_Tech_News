"""
In this file the basic back-end is created and launched. It is used to control the news bot.
Author: Cornelius Wolff
eMail: cowolff@uos.de
"""

from flask import Flask, render_template, redirect, url_for, request
from Database import Data
from Update import send_message
import threading
from Amazon import start, check_single_price
import time
from ProcessManager import ProcessManager

api = ""  # The API-Key for the Telegram Bot
chat_ids = ["653734838"]    # List of chat ids which want to be updated
app = Flask(__name__)
sessions = []   # Login Sessions for the backend

database = Data()
#database.add_amazon_product("Lenovo Tab P12","B09L61QRM1")


# The base route either redirects to the login screen or to the home screen.
@app.route('/')
def base():
    if request.remote_addr in sessions:
        return redirect(url_for("getHome"))
    else:
        return redirect(url_for("getLogin"))


# Login path for signining into the back-end.
@app.route('/login', methods=['GET', 'POST'])
def getLogin():
    data = Data()
    error = None
    if request.method == 'POST':
        if data.check_password(request.form['username'], request.form['password']):
            sessions.append({"ip": request.remote_addr, "username": request.form['username']})
            return redirect(url_for('getHome'))
        else:
            error = "Invalid username or password"
    return render_template('login.html', error=error)


# The home link shows an overview of the tracked products and the number of news tips sent.
@app.route('/home')
def getHome():
    ips = [x["ip"] for x in sessions]
    if request.remote_addr in ips:  # Checks if the browser is logged in
        name = sessions[ips.index(request.remote_addr)]["username"]     # Returns the username for the current user

        data = Data()
        products = data.get_overview_products()
        # products = [{"name":"Galaxy M21", "asin":"TEST", "lastUpdate":"0", "price":"192,00€", "change":"+3%"}]
        test = [213, 415, 200, 214, 213, 413, 200]
        labels = [1640449288, 1640458256, 1640468256, 1640478256, 1640488256, 1640948256, 1641448256]
        numberOfNews = [12, 11, 5, 3, 9]
        weeksNumbers = [41, 42, 43, 44, 45]
        return render_template('index.html', products=products, prices=test, labels=labels, numberOfNews=numberOfNews, weeksNumbers=weeksNumbers, name=name)
    else:
        return redirect(url_for('getLogin'))


# An overview of every issue that came up grouped into 3 classes.
@app.route('/issues',  methods=['GET', 'POST'])
def getIssueList():
    ips = [x["ip"] for x in sessions]
    if request.remote_addr in ips:
        # issues = [{"process":"Amazon", "problem":"Exception during crawl at product TRDJEM", "time":"12.12.2021 18:01", "file":"Amazon.py", "line":"12-17", "severity":3}, {"process":"Telegram", "problem":"Exception during sending in chat 12", "time":"12.12.2021 15:01", "file":"Telegram.py", "line":"10-19", "severity":2}]
        data = Data()
        issues = data.get_Issues()
        name = sessions[ips.index(request.remote_addr)]["username"]
        if request.method == 'GET':
            return render_template("issues.html", issues=issues, name=name)
        elif request.method == "POST":
            if request.form.get('Solved-Button') == 'Solved':
                # data.solvedIssue()
                return render_template("issues.html", issues=issues, name=name)
            if request.form.get('Reload-Button') == 'Reload':
                return render_template('issues.html', issues=issues, name=name)
    else:
        return redirect(url_for('getLogin'))


# An overview of every process, its status and its last update.
@app.route('/processes')
def getProcesses():
    ips = [x["ip"] for x in sessions]
    if request.remote_addr in ips:
        name = sessions[ips.index(request.remote_addr)]["username"]
        processes = [{"name":"Amazon Crawler", "lastChange":"16.12.2021 12:01", "lastError":"13.12.2021 12:30", "running":True}, {"name":"Telegram Bot", "lastChange":"22.12.2021 12:01", "lastError":"14.12.2021 12:30", "running":False}]
        return render_template("processList.html", processes=processes, name=name)
    else:
        return redirect(url_for('getLogin'))


# A list of all individual products which are specificly tracked
@app.route('/amazon/products', methods=['GET', 'POST'])
def getAmazonProductList():
    ips = [x["ip"] for x in sessions]
    if request.remote_addr in ips:
        name = sessions[ips.index(request.remote_addr)]["username"]
        data = Data()
        # products = [{"name":"Galaxy M21", "asin":"DGXT5RR", "price":"200.45€", "lastUpdate":"13.12.2021", "change":"+7%"}, {"name":"Galaxy S20 FE", "asin":"DEUU5RR", "price":"421.45€", "lastUpdate":"13.12.2021", "change":"+3%"}]
        if request.method == 'GET':
            products = data.get_overview_products()
            return render_template("amazon-products-overview.html", products=products, name=name)
        if request.method == 'POST':
            if request.form.get('AsinAddButton') == "Add":
                asin = request.form['asinTextInput']
                print("Term:" + asin)
                term = request.form['asinNameInput']
                if term == "":
                    product = check_single_price(asin, data)
                    term = product["title"]
                    data.add_amazon_price(asin, product["price"], time.time())
                data.add_amazon_product(term, asin)
                data.add_amazon_watchlist(asin)
                products = data.get_overview_products()
                return render_template("amazon-products-overview.html", products=products, name=name)
            if request.form.get('Reload-Button') == "Reload":
                products = data.get_overview_products()
                return render_template("amazon-products-overview.html", products=products, name=name)
    else:
        return redirect(url_for('getLogin'))


# A list of all search terms which are tracked
@app.route('/amazon/terms', methods=['GET', 'POST'])
def getAmazonTermList():
    ips = [x["ip"] for x in sessions]
    if request.remote_addr in ips:
        name = sessions[ips.index(request.remote_addr)]["username"]

        terms = [{"term":"Samsung Galaxy", "numberProducts":12, "singleProducts":5, "lastUpdate":"14.12.2021"}, {"term":"Huawei", "numberProducts":12, "singleProducts":3, "lastUpdate":"14.12.2021"}]
        data = Data()
        if request.method == 'GET':
            terms = data.get_Term_Overview()
            return render_template('amazon-terms-overview.html', terms=terms, name=name)
        if request.method == 'POST':
            if request.form.get('TermAddButton') == "Add":
                term =  request.form['newTerm']
                data.add_amazon_search_term(term)
                terms = data.get_Term_Overview()
                return render_template('amazon-terms-overview.html', terms=terms, name=name)
            else:
                terms = data.get_Term_Overview()
                return render_template('amazon-terms-overview.html', terms=terms, name=name)
    else:
        return redirect(url_for('getLogin'))


# A list of all rss feeds that are beeing tracked, when they were last updated, how many news are stored and how many of them were relevant
@app.route('/rss',  methods=['GET', 'POST'])
def getRSSOverview():
    ips = [x["ip"] for x in sessions]
    if request.remote_addr in ips:
        data = Data()
        name = sessions[ips.index(request.remote_addr)]["username"]
        # feeds = [{"name":"Winfuture", "numberNews":121, "numberRelevantNews":6, "numberRelevantNewsToday":2, "lastUpdate":"11.16.2021 8:21"}, {"name":"TheVerge", "numberNews":98, "numberRelevantNews":8, "numberRelevantNewsToday":2, "lastUpdate":"11.16.2021 8:25"}]
        feeds = data.get_RSS_Feeds()
        if request.method == 'GET':
            return render_template('rss-overview.html', feeds=feeds, name=name)
        if request.method == 'POST':
            if request.form.get('RSSAdd') == "Add":
                link = request.form['linkRSSField']
                title = request.form['nameRSSField']
                if(title == "" or link == ""):
                    return render_template('rss-overview.html', feeds=feeds, name=name)
                data.add_RSS_Feed(link, title)
                return render_template('rss-overview.html', feeds=feeds, name=name)
            elif request.form.get('SpecificRSSButton'):
                return redirect(url_for('getRSSspecific', feedId=request.form.get('SpecificRSSButton')))
    else:
        return redirect(url_for('getLogin'))

@app.route('/rss/<feedId>', methods=['GET', 'POST'])
def getRSSspecific(feedId):
    ips = [x["ip"] for x in sessions]
    if request.remote_addr in ips:
        data = Data()
        name = sessions[ips.index(request.remote_addr)]["username"]

        if request.method == 'GET':
            link, title = data.get_RSS_Link_Title(feedId)
            newsfeed = data.get_RSS_News(link)
            return render_template('rss-specific.html', newsfeed=newsfeed, name=name, title=title, link=link)
        if request.method == 'POST':
            link, title = data.get_RSS_Link_Title(feedId)
            newsfeed = data.get_RSS_News(link)
            return render_template('rss-specific.html', newsfeed=newsfeed, name=name, title=title, link=link)
#x = threading.Thread(target=start, args=(api, chat_ids), daemon=True)
#x.start()

processManager = ProcessManager(api, chat_ids)