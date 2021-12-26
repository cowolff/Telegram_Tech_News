from Database import Data
from Update import get_update, send_message
from Amazon import start
from threading import Thread
data = Data()
api = "1719127362:AAHSCLN1M5BoGg3pt3AUYz0MH7W8uPvIcfY"
chat_ids = ["653734838"]

x = Thread(target=start, args=(api, chat_ids), daemon=True)
#x.start()

def add_amazon(content):
    pass

def remove_amazon(content):
    pass

def add_rss(content):
    pass

def remove_rss(content):
    pass

def add_rss_keyword(feed, keyowrd):
    pass

def remove_rss_keyword(feed, keyowrd):
    pass

if __name__ == "__main__":
    while True:
        try:
            statement = input("Enter your command: (-H/-Help for list of commands)")
            split = statement.split(" ")
            if "-H" in statement or "-Help" in statement:
                print("-RSS:{\n    -add: adds a new rss feed\n    -remove: removes an existing rss feed\n    -keyowrds:\n    {\n        -add: adds a new keyword for this rss feed\n        -remove: removes a keyword for this rss feed\n    }\n}")
                print("-Amazon:{\n    -product [-add/-remove]: adds or removes a amazon product\n    -term [-add/-remove]: adds or removes a search term\n}")
            elif split[0] == "-RSS":
                if split[1] == "-add":
                    add_rss(split[2])
                elif split[1] == "-remove":
                    remove_rss(split[2])
                elif split[3] == "-keyword":
                    if split[4] == "-add":
                        add_rss_keyword(split[5])
                    elif split[4] == "-remove":
                        remove_rss_keyword(split[5])

        except KeyboardInterrupt:
            exit(0)