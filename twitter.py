from Database import Data
import requests

def twitter_process():
    while True:
        # data = Data()
        barer = "AAAAAAAAAAAAAAAAAAAAABXDjgEAAAAA9WPmKl6dcZ17e%2BKhjVjIGYDiUT0%3DlgwetRF78spSTSk0eE61GbclDuENjuKuAo1igVT5VEyDHZv0NK"
        username = "cowolff"
        headers = {"Authorization": "Bearer {}".format(barer)}
        url = f"https://api.twitter.com/2/users/by/username/{username}"
        response = requests.request("GET", url, headers = headers)
        print(response.content["data"]["id"])
        break

twitter_process()