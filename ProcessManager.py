import time
from Database import Data
import multiprocessing
from datetime import datetime, timedelta
import threading
from Update import send_message_to_chats
from Amazon import amazon_process
from RSS_Feed import rss_process
from twitter import twitter_process
import random

class ProcessManager():

    amazon_crawler = False
    rss = False
    twitter = False

    def __init__(self, chat_ids):

        self.__data = Data()
        self.chat_ids = chat_ids
        self.__amazonProcess = threading.Thread(target=amazon_process, daemon=True)
        self.__rssProcess = threading.Thread(target=rss_process, daemon=True)
        self.__twitterProcess = threading.Thread(target=twitter_process, daemon=True)

        self.x = threading.Thread(target=self.__checkStatus, daemon=True)

    def start(self):
        self.__amazonProcess.start()
        self.__rssProcess.start()
        self.__twitterProcess.start()
        self.x.start()

    def check_process(self, process, is_running, function, is_current, name):
        if not process.is_alive():
            is_running = False
            process = threading.Thread(target=function, daemon=True)
            process.start()
            if not is_current:
                is_current = True
                self.__data.add_Issue("Process Manager", name + " process failed", "ProcessManager.py", "0-0", 1)
                send_message_to_chats(name + " failed", self.chat_ids, self.api_key)
        else:
            is_current = False
            self.is_running = True

    def __checkStatus(self):
        current_incident_amazon = False
        current_incident_rss = False
        current_incident_twitter = False
        while True:
            time.sleep(30)
            self.check_process(self.__amazonProcess, self.amazon_crawler, amazon_process, current_incident_amazon, "Amazon Crawler")
            self.check_process(self.__rssProcess, self.rss, rss_process, current_incident_rss, "RSS Crawler")
            self.check_process(self.__twitterProcess, self.twitter, twitter_process, current_incident_twitter, "Twitter Crawler")

    def numberNotRunning(self):
        i = 0
        for process in [self.__amazonProcess, self.__rssProcess]:
            if not process.is_alive():
                i = i + 1
        return i

    def restartProcesses(self):
        if not self.__amazonProcess.is_alive():
            self.__amazonProcess = threading.Thread(target=amazon_process, daemon=True)
            self.__amazonProcess.start()
        if not self.__rssProcess.is_alive():
            self.__rssProcess = threading.Thread(target=rss_process, daemon=True)
            self.__rssProcess.start()
        if not self.__twitterProcess.is_alive():
            self.__twitterProcess = threading.Thread(target=twitter_process, daemon=True)
            self.__twitterProcess.start()