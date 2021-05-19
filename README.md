# RSS_Telegram_News
I wrote this little script for me to constantly run on a raspberry pi.

It basicly takes all the RSS Feeds which are stored in the *config.txt* file and sends them via the Telegram bot. But because some rss feeds are also posting stuff which is of no interest to me, i also build in a function to filter for certain tags. If no tags are handed in it sends all posts from the rss feed.

Furthermore i added the feature to filter for keywords in the title. Note that if you use keywords and tags there has to be an overlap where at least one tag and one keyword is true. If you want to get around this at the moment you have to add the same source twice in the config.
