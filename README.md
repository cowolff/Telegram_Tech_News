# RSS_Telegram_News
Originally this was supposed to be a small script to automaticly fetch RSS_Feeds every x minutes, do some keyword matching and send relevant news via Telegram. Now this has become a bit more than that, but the base functionality is still the same. I just decided to also implement an entire web backend, where I can add and remove RSS Links, change keywords and tags for filtering and in general get a better overview of what is happening. At the moment I manage about 40 RSS Feeds with this program.

If you want to try it yourself, you simply have to pull this repo on your linux machine and start the program by using this command in the base folder of the repo
```
flask run --host=0.0.0.0
```
Obviously you need to install all used libraries first. Please note that this is not a finished product and you should NOT make this accessible to the open web!!!! I do not take responsibility for any security flaws because there will be a lot of those. Besides there are still some buttons which are not fully implemented and will return 404 errors (though this should not crash the server at any point). This is simply a small program I designed managing all of my RSS feeds and should ONLY be accessible from within the local network.

The name of the standard user is cowolff and the password is 1234567. This is how the interace of the RSS-Back-end looks:
![image](https://github.com/cowolff/Telegram_Tech_News/blob/main/Screenshot/RSSFeeds.JPG)
