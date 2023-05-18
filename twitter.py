from Database import Data
import requests
import time

def twitter_process():
    while True:
        # data = Data()
        barer = ""
        username = "cowolff"
        headers = {"Authorization": "Bearer {}".format(barer)}
        url = f"https://api.twitter.com/2/users/by/username/{username}"
        response = requests.request("GET", url, headers = headers)
        print(response.content)
        break

twitter_process()

def get_initial_data(username):
    data = Data()
    barer = data.get_twitter_baerer()
    if barer == None:
        return None
    try:
        headers = {"Authorization": "Bearer {}".format(barer)}
        url = f"https://api.twitter.com/2/users/by/username/{username}"
        response = requests.request("GET", url, headers = headers)
        response_data = response.json()["data"]
        data.add_twitter_feed(response_data["username"], response_data["id"])
        get_tweets(response_data["id"])
    except:
        return None

def get_tweets(userId):
    data = Data()
    barer = data.get_twitter_baerer()
    if barer == None:
        return None
    try:
        headers = {"Authorization": "Bearer {}".format(barer)}
        url = f"https://api.twitter.com/2/users/{userId}/tweets"
        response = requests.request("GET", url, headers = headers)
        response_data = response.json()["data"]
        timestamp = int(time.time())
        for tweet in response_data:
            data.add_tweet(tweet["id"], userId, tweet["text"], timestamp)
    except:
        return None
