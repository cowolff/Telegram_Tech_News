"""
In this file the basic back-end is created and launched. It is used to control the news bot.
Author: Cornelius Wolff
eMail: cowolff@uos.de
"""

from flask import Flask, render_template, redirect, url_for, request, Response
import csv
from Database import Data
from Update import send_message
from Amazon import start, check_single_price
from ProcessManager import ProcessManager
from RSS_Feed import process_news, determine_send
from datetime import datetime
from twitter import get_initial_data
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)

app = Flask(__name__)
app.secret_key = 'test12345'
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.login_message_category = "info"
login_manager.init_app(app)

users = {}

class User(UserMixin):
    def __init__(self, authenticated, active, anonymous, id) -> None:
        self.authenticated = authenticated
        self.active = active
        self.anonymous = anonymous
        self.id = id

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return self.active

    def is_anonmyous(self):
        return self.anonymous

    def get_id(self):
        return self.id
    
@app.route('/')
@login_required
def base():
    return redirect(url_for("getHome"))
    
# Login path for signining into the back-end.
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        database = Data()
        username = request.form['username']
        password = request.form['password']

        if database.check_password(username, password):
            user = User(True, True, False, username)
            users[username] = user
            login_user(user)
            return redirect(url_for("getHome"))
    error = None
    return render_template('login.html', error=error)

# The home link shows an overview of the tracked products and the number of news tips sent.
@app.route('/home')
@login_required
def getHome():
    name = current_user.get_id()
    data = Data()
    products = data.get_overview_products()
    products, prd_labels, prd_prices, bar_counts, bar_dates, today_count, forwarded_count, share = data.get_home()
    processesNotRunning = processManager.numberNotRunning()
    return render_template('index.html', products=products, prices=prd_prices, labels=prd_labels, numberOfNews=bar_counts, weeksNumbers=bar_dates, name=name, numberNewsGathered=today_count, numberNewsForwarded=forwarded_count, processesNotRunning=processesNotRunning, shareAcceptance=share)

# An overview of every issue that came up grouped into 3 classes.
@app.route('/issues',  methods=['GET', 'POST'])
@login_required
def getIssueList():
    data = Data()
    issues = data.get_Issues()
    name = current_user.get_id()
    if request.method == 'GET':
        return render_template("issues.html", issues=issues, name=name)
    elif request.method == "POST":
        if request.form.get('Solved-Button') == 'Solved':
            return render_template("issues.html", issues=issues, name=name)
        if request.form.get('Reload-Button') == 'Reload':
            return render_template('issues.html', issues=issues, name=name)
        
# An overview of every process, its status and its last update.
@app.route('/processes')
@login_required
def getProcesses():
    name = current_user.get_id()
    processes = [{"name":"Amazon Crawler", "lastChange":"16.12.2021 12:01", "lastError":"13.12.2021 12:30", "running":True}, {"name":"Telegram Bot", "lastChange":"22.12.2021 12:01", "lastError":"14.12.2021 12:30", "running":False}]
    return render_template("processes.html", processes=processes, name=name)

# A list of all individual products which are specificly tracked
@app.route('/amazon/', methods=['GET', 'POST'])
@login_required
def getAmazonProductList():
    name = current_user.get_id()
    data = Data()
    if request.method == 'GET':
        products = data.get_overview_products()
        return render_template("amazon.html", products=products, name=name)
    if request.method == 'POST':
        if request.form.get('AsinAddButton') == "Add":
            asin = request.form['asinTextInput']
            term = request.form['asinNameInput']
            if term == "":
                product = check_single_price(asin, data)
                term = product["title"]
                data.add_amazon_price(asin, product["price"], time.time())
            data.add_amazon_product(term, asin)
            data.add_amazon_watchlist(asin)
            products = data.get_overview_products()
            return render_template("amazon.html", products=products, name=name)
        if request.form.get('Reload-Button') == "Reload":
            products = data.get_overview_products()
            return render_template("amazon.html", products=products, name=name)
        
# A list of all search terms which are tracked
@app.route('/amazon/terms', methods=['GET', 'POST'])
@login_required
def getAmazonTermList():
    name = current_user.get_id()
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
        
@app.route('/amazon/add', methods=['POST'])
@login_required
def addAmazonASIN():
    return redirect(url_for("getAmazonTermList"))

# A list of all rss feeds that are beeing tracked, when they were last updated, how many news are stored and how many of them were relevant
@app.route('/rss',  methods=['GET', 'POST'])
@login_required
def getRSSOverview():
    data = Data()
    name = current_user.get_id()
    feeds = data.get_RSS_Overview()
    if request.method == 'GET':
        return render_template('rss.html', feeds=feeds, name=name)
    if request.method == 'POST':
        if request.form.get('RSSAdd') == "Add":
            link = request.form['linkRSSField']
            title = request.form['nameRSSField']
            language = request.form['languageInput']
            if(title == "" or link == "" or language == "Choose a language"):
                return render_template('rss.html', feeds=feeds, name=name)
            data.add_RSS_Feed(link, title, language)
            feeds = data.get_RSS_Overview()
            return render_template('rss.html', feeds=feeds, name=name)
        if request.form.get('Reload-Button') == "Reload":
            api = data.get_api_key()["api_key"]
            process_news(api)
            feeds = data.get_RSS_Overview()
            return render_template('rss.html', feeds=feeds, name=name)
        elif request.form.get('SpecificRSSButton'):
            return redirect(url_for('getRSSspecific', feedId=request.form.get('SpecificRSSButton')))
        
@app.route('/rss/download', methods=["GET"])
def downloadRSS():
    data = Data()
    csv_data = data.getDownloadNews()
    with open('data.csv', "w", newline='', encoding='utf-8') as outputfile:
        keys = csv_data[0].keys()
        dict_writer = csv.DictWriter(outputfile, keys)
        dict_writer.writeheader()
        dict_writer.writerows(csv_data)
    with open("data.csv") as fp:
        csv_data = fp.read()
        return Response(csv_data, mimetype="text/csv", headers={"Content-disposition":"attachment; filename=data.csv"})
    
@app.route('/rss/download/<feedId>', methods=["GET"])
@login_required
def downloadRSSspecific(feedId):
    data = Data()
    link, title = data.get_RSS_Link_Title(feedId)
    newsfeed = data.get_RSS_News(link, title)
    with open('data.csv', "w", newline='', encoding='utf-8') as outputfile:
        keys = newsfeed[0].keys()
        dict_writer = csv.DictWriter(outputfile, keys)
        dict_writer.writeheader()
        dict_writer.writerows(newsfeed)
    with open("data.csv") as fp:
        csv_data = fp.read()
        return Response(csv_data, mimetype="text/csv", headers={"Content-disposition":"attachment; filename=data.csv"})
    
def getRSSSpecificPage(feedId, data, name, filter: bool):
    link, title, active = data.get_RSS_Link_Title(feedId)
    newsfeed = data.get_RSS_News(link, title)
    keywords = data.get_rss_keywords(feedId)
    tags = data.get_rss_tags(feedId)
    if filter:
        newsfeed = [x for x in newsfeed if determine_send(x["title"], x["tags"], feedId, data)]
    newsfeed = [{"title":x["title"], "tags":x["tags"], "timestamp":datetime.fromtimestamp(float(x["timestamp"])).strftime("%d/%m/%Y, %H:%M:%S"), "name":x["name"], "relevance":x["relevance"]} for x in newsfeed]
    return render_template('rss-specific.html', newsfeed=newsfeed, name=name, title=title, link=link, id=feedId, keywords=keywords, tags=tags, feedId=feedId, active=active)
    
@app.route('/rss/<feedId>', methods=['GET', 'POST'])
@login_required
def getRSSspecific(feedId):
    data = Data()
    name = current_user.get_id()

    if request.method == 'GET':
        return getRSSSpecificPage(feedId, data, name, False)

    if request.method == 'POST':
        if request.form.get('Reload-Button') == "Reload Feed":
            title, link, active = data.get_RSS_Link_Title(feedId)
            api = data.get_api_key()["api_key"]
            process_news(api)
            return getRSSSpecificPage(feedId, data, name, False)

        if request.form.get('filterNews') == "Filter for keywords and tags":
            return getRSSSpecificPage(feedId, data, name, True)

        if request.form.get('keywordAddButton') == "Add":
            keyword = request.form.get('keywordAddField').lower()
            if keyword != "":
                data.add_rss_keyword(feedId, keyword)
                return getRSSSpecificPage(feedId, data, name, False)

        if request.form.get('removeTag'):
            tag = request.form.get('removeTag').lower()
            data.remove_rss_tag(feedId, tag)
            return getRSSSpecificPage(feedId, data, name, False)

        if request.form.get('removeKeyword'):
            keyword = request.form.get('removeKeyword').lower()
            data.remove_rss_keyword(feedId, keyword)
            return getRSSSpecificPage(feedId, data, name, False)

        if request.form.get('tagAddButton') == "Add":
            tag = request.form.get('tagAddField').lower()
            if tag != "":
                data.add_rss_tag(feedId, tag)
                return getRSSSpecificPage(feedId, data, name, False)

        else:
            return getRSSSpecificPage(feedId, data, name, False)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def getSettings():
    data = Data()
    userName = current_user.get_id()
    api_key = data.get_api_key()["api_key"]
    if request.method == 'POST':
        if request.form.get('APIKey') == "Update":
            if request.form.get('apiKeyInput') == "":
                return render_template('settings.html', name=userName, api_key=api_key, id=userName)
            else:
                key = request.form.get('apiKeyInput')
                data.update_api_key(key)
                api_key = data.get_api_key()["api_key"]
                return render_template('settings.html', name=userName, api_key=api_key, id=userName)
    return render_template('settings.html', name=userName, api_key=api_key, id=userName)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def getProfile():
    data = Data()
    if request.method == 'GET':
        current_mail, current_mail_server, current_mail_port = data.get_email_account()
        return render_template('profile.html', current_mail=current_mail, current_mail_server=current_mail_server, current_mail_port=current_mail_port)
    
@app.route('/api/rss/priority', methods=['POST'])
@login_required
def updatePriority():
    try:
        content = request.get_json()
        data = Data()
        for article in content:
            title = article["title"]
            tags = article["tags"]
            priority = article["priority"]
            data.update_priority(title, tags, priority)
        return "Update successful"
    except:
        return "Update failed"
    
@app.route('/email')
@login_required
def getEmailOverview():
    return render_template('email_overview.html')

@app.route('/email/download')
@login_required
def downloadEmailNews():
    return redirect(url_for("getHome"))

@app.route('/twitter')
@login_required
def getTwitterOverview():
    data = Data()
    feeds = data.get_twitter_overview()
    return render_template('twitter.html', feeds=feeds)

@app.route('/twitter/<twitterId>', methods=['GET'])
@login_required
def getTwitterSpecific(twitterId):
    data = Data()
    return redirect(url_for("getTwitterOverview"))
        

@app.route('/twitter/add', methods=['POST'])
@login_required
def addTwitterFeed():
    if request.form.get('username') != "":
        data = Data()
        twitter = request.form.get('username')
        get_initial_data(twitter)
        return redirect(url_for("getTwitterOverview"))
    else:
        return redirect(url_for("getTwitterOverview"))

@app.route('/twitter/download/<feedId>', methods=['POST'])
@login_required
def downloadFeed():
    pass

@app.route('/twitter/unfollow/<feedId>', methods=['POST'])
@login_required
def unfollow(feedId):
    pass

@app.route('/twitter/follow/<feedId>', methods=['POST'])
@login_required
def follow(feedId):
    pass

@app.route('/profile/email', methods=['POST'])
@login_required
def updateMailData():
    if request.form.get('email') == '' or request.form.get('mail_password') == '' or request.form.get('mail_server') == '' or request.form.get('mail_port') == '':
        return redirect(url_for("getProfile"))
    else:
        data = Data()
        current_mail = request.form.get('email')
        password_mail = request.form.get('mail_password')
        mail_server = request.form.get('mail_server')
        mail_port = request.form.get('mail_port')
        data.update_email_account(current_mail, password_mail, mail_server, mail_port)
        return redirect(url_for("getProfile"))

@app.route('/profile/data/update/telegram', methods=['POST'])
@login_required
def updateTelegramData():
    data = Data()
    if request.form.get('telegram_key') == "":
        return redirect(url_for("getProfile"))
    else:
        telegram = request.form.get('telegram_key')
        data.update_telegram_token(telegram)
        return redirect(url_for("getProfile"))

@app.route('/profile/data/update/signal', methods=['POST'])
@login_required
def updateSignalData():
    data = Data()
    if request.form.get('signal_key') == "":
        return redirect(url_for("getProfile"))
    else:
        signal = request.form.get('signal_key')
        data.update_signal_api(signal)
        return redirect(url_for("getProfile"))

@app.route('/profile/data/update/twitter', methods=['POST'])
@login_required
def updateTwitterData():
    data = Data()
    if request.form.get('twitter_key') == "":
        return redirect(url_for("getProfile"))
    else:
        twitter = request.form.get('twitter_key')
        data.update_twitter_api(twitter)
        return redirect(url_for("getProfile"))

@app.route('/profile/data/rss')
@login_required
def getRSSData():
    return redirect(url_for("getProfile"))

@app.route('/profile/data/mail')
@login_required
def getMailData():
    return redirect(url_for("getProfile"))

@app.route('/profile/data/price')
@login_required
def getPriceData():
    return redirect(url_for("getProfile"))

@app.route('/profile/data/delete')
@login_required
def deleteDataset():
    return redirect(url_for("getProfile"))

@app.route('/ML')
@login_required
def getMLOverview():
    return render_template('ML.html')

@app.route('/website')
@login_required
def getWebsiteChange():
    return render_template('website-change.html')

@app.route('/website/add')
@login_required
def addWebsiteChange():
    return redirect(url_for("getWebsiteChange"))

@login_manager.user_loader
def load_user(user_id):
    if user_id in users.keys():
        return users[user_id]
    else:
        return None

if __name__ == '__main__':
    chat_ids = ["653734838"]
    processManager = ProcessManager(chat_ids)
    processManager.start()
    app.run()