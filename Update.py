import sqlite3
import requests
from Database import Data
import time

def get_update():
    data = Data()
    chats = data.get_chats()
    api_key = data.get_api_key()["api_key"]
    print(chats)

    json = requests.post(f'https://api.telegram.org/bot{api_key}/getUpdates').json()
    try:
        print(json)
        new_chats = [x["message"]["chat"]["id"] for x in json["result"] if "unsubscribe" not in x["message"]["text"]]
        remove_chats = [x["message"]["chat"]["id"] for x in json["result"] if "unsubscribe" in x["message"]["text"]]
        new_chats = [x for x in new_chats if str(x) not in chats]
        new_chats = list(dict.fromkeys(new_chats))
        data.add_chats(new_chats)
        if len(new_chats) > 0:
            data = Data()
            api_key = data.get_api_key()["api_key"]
            if api_key != "no_value":
                for chat in new_chats:
                    message = "Subscription confirmed"
                    requests.get(f'https://api.telegram.org/bot{api_key}/sendMessage?chat_id={chat}&text={message}')
        data.remove_chats(remove_chats)
    except Exception as e:
        print(e)

def send_message(message, chat_id, api_key, news_key, type):
    timestamp = time.time()
    data = Data()
    data.add_news_tipp(news_key, type, timestamp)
    requests.get(f'https://api.telegram.org/bot{api_key}/sendMessage?chat_id={chat_id}&text={message}')

def send_message_to_chats(message, chat_ids, api_key, news_key, type):
    timestamp = time.time()
    data = Data()
    data.add_news_tipp(news_key, type, timestamp)
    for chat_id in chat_ids:
        requests.get(f'https://api.telegram.org/bot{api_key}/sendMessage?chat_id={chat_id}&text={message}')