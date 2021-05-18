# RSS_Telegram_News
I wrote this little script for me to constantly run on a raspberry pi.

It basicly takes all the RSS Feeds which are stored in the config file and sends them via the Telegram bot. But because some rss feeds are also posting stuff which is of no interest to me, i also build in a function to filter for certain tags. If no tags are handed in it sends all posts from the rss feed.
