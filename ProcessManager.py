import time
from Database import Data
import multiprocessing
from datetime import datetime, timedelta
import threading
from Update import send_message_to_chats
from Amazon import amazon_process
import random

class ProcessManager():

    amazon_crawler = False
    rss = False

    def __init__(self, api, chat_ids):

        self.__data = Data()
        self.chat_ids = chat_ids
        self.api_key = api
        self.__amazonProcess = threading.Thread(target=amazon_process, daemon=True, args=(self.api_key, self.chat_ids))

        # self.__rssProcess = threading.Thread(target=__rss_process, daemon=True)
        # self.__rssProcess.start()

        self.x = threading.Thread(target=self.__checkStatus, daemon=True)

    def start(self):
        self.__amazonProcess.start()
        self.x.start()

    def __rss_process(self):
        pass

    def check_process(self, process, is_running, is_current, name):
        if not process.is_alive():
            is_running = False
            process = multiprocessing.Process(target=self.__amazon_process,daemon=True)
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
        while True:
            time.sleep(30)
            self.check_process(self.__amazonProcess, self.amazon_crawler, current_incident_amazon, "Amazon Crawler")
            # self.check_process(self.__rssProcess, self.rss, current_incident_rss, "RSS Feed")