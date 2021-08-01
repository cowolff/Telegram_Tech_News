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
        cur.execute('''CREATE TABLE IF NOT EXISTS RSS_News(title TEXT PRIMARY KEY, Timestamp TEXT)''')
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