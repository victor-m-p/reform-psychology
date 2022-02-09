import requests
import os
import json
import pandas as pd
import csv
import datetime
import unicodedata
import time
import re 
import ndjson

# check whether we can get geo.
# check whether we can make 1 ndjson file (user + tweet + geo). 
# check whether we can get the full tweets for retweets. 
 
# Opening JSON file
with open('/work/50114/twitter/data/json/2020-01-01_openscience_1_tweet.json') as json_file:
    jsonfile = json.load(json_file)

data_obj = json.get("data")
users_obj = json.get("includes").get("users") # 
places_obj = json.get("includes").get("places") # 
json.get("includes").get("crated_at")
json.get("includes")
data_obj[0]
for row in places_obj: 
    #print(row)
    row["name"]
    row[""]


referenced['text'] for referenced in tweet['referenced_tweets'] if referenced['type'] == 'retweeted')

{"conversation_id": "1365618709222600705", "text": "RT @tradehunter305: While checking into my hotel, I seen this light skin dude behind me. We ended up on the same floor, I asked him if he w\u2026", "reply_settings": "everyone", "possibly_sensitive": false, "source": "Twitter for iPhone", "public_metrics": {"retweet_count": 1256, "reply_count": 0, "like_count": 0, "quote_count": 0}, "lang": "en", "referenced_tweets": [{"type": "retweeted", "id": "1353880904188506112", "entities": {"urls": [{"start": 274, "end": 297, "url": "https://t.co/9CovM6hF9P", "expanded_url": "https://twitter.com/tradehunter305/status/1353880904188506112/video/1", "display_url": "pic.twitter.com/9CovM6hF9P"}], "hashtags": [{"start": 228, "end": 243, "tag": "tradehunter305"}, {"start": 244, "end": 256, "tag": "miamifreaks"}], "annotations": [{"start": 134, "end": 141, "probability": 0.5495, "type": "Person", "normalized_text": "Ofocurse"}], "mentions": [{"start": 178, "end": 191, "username": "_BDhandsome1"}, {"start": 257, "end": 273, "username": "tradehunter_305"}]}, "conversation_id": "1353880904188506112", "text": "While checking into my hotel, I seen this light skin dude behind me. We ended up on the same floor, I asked him if he wanted to smoke Ofocurse he agreed. Come to find out it was @_BDhandsome1 I had to eat that pretty dick up \ud83d\udc45\ud83c\udf46 #tradehunter305 #miamifreaks @tradehunter_305 https://t.co/9CovM6hF9P", "reply_settings": "everyone", "possibly_sensitive": true, "source": "Twitter for iPhone", "attachments": {"media_keys": ["7_1353879826868875264"], "media": [{}]}, "public_metrics": {"retweet_count": 1256, "reply_count": 23, "like_count": 4509, "quote_count": 23}, "lang": "en", "created_at": "2021-01-26T01:42:16.000Z", "author_id": "63184818", "geo": {"place_id": "04cb31bae3b3af93"}, "author": {"url": "https://t.co/zsgog6bssy", "name": "Beast", "pinned_tweet_id": "1353880904188506112", "public_metrics": {"followers_count": 33671, "following_count": 360, "tweet_count": 6666, "listed_count": 78}, "location": "Miami, FL", "entities": {"url": {"urls": [{"start": 0, "end": 23, "url": "https://t.co/zsgog6bssy", "expanded_url": "https://onlyfans.com/tradehunter305", "display_url": "onlyfans.com/tradehunter305"}]}}, "id": "63184818", "protected": false, "username": "tradehunter305", "description": "HAITIAN NIGGA \ud83c\udded\ud83c\uddf9 big dick, fat ass, deepthroat. I\u2019m Vtop that love to suck \ud83c\udf46 and fuck \ud83c\udf51. follow back up page tradehunter_305", "verified": false, "profile_image_url": "https://pbs.twimg.com/profile_images/1181809641124237312/RBOiw6OA_normal.jpg", "created_at": "2009-08-05T16:48:42.000Z"}}], "id": "1365618709222600705", "created_at": "2021-02-27T11:04:06.000Z", "author_id": "867867068988874752", "entities": {"mentions": [{"start": 3, "end": 18, "username": "tradehunter305", "url": "https://t.co/zsgog6bssy", "name": "Beast", "pinned_tweet_id": "1353880904188506112", "public_metrics": {"followers_count": 33671, "following_count": 360, "tweet_count": 6666, "listed_count": 78}, "location": "Miami, FL", "entities": {"url": {"urls": [{"start": 0, "end": 23, "url": "https://t.co/zsgog6bssy", "expanded_url": "https://onlyfans.com/tradehunter305", "display_url": "onlyfans.com/tradehunter305"}]}}, "id": "63184818", "protected": false, "description": "HAITIAN NIGGA \ud83c\udded\ud83c\uddf9 big dick, fat ass, deepthroat. I\u2019m Vtop that love to suck \ud83c\udf46 and fuck \ud83c\udf51. follow back up page tradehunter_305", "verified": false, "profile_image_url": "https://pbs.twimg.com/profile_images/1181809641124237312/RBOiw6OA_normal.jpg", "created_at": "2009-08-05T16:48:42.000Z"}]}, "author": {"url": "", "name": "Gooddae", "public_metrics": {"followers_count": 227, "following_count": 1378, "tweet_count": 10233, "listed_count": 1}, "location": "Atlanta, GA", "entities": {"description": {"hashtags": [{"start": 61, "end": 65, "tag": "ATL"}, {"start": 66, "end": 71, "tag": "BEAR"}, {"start": 83, "end": 91, "tag": "JUSTFUN"}]}}, "id": "867867068988874752", "protected": false, "username": "Gooddae80", "description": "Just here for the entertainment and reposting what I like... #ATL #BEAR I guess... #JUSTFUN add my switch code SW-5138-3277-6701", "verified": false, "profile_image_url": "https://pbs.twimg.com/profile_images/1208330683371937792/mTfONoQU_normal.jpg", "created_at": "2017-05-25T22:16:48.000Z"}}


tweet = {
    "conversation_id": "1365618709222600705", 
    "text": "RT @tradehunter305: While checking into my hotel, I seen this light skin dude behind me. We ended up on the same floor, I asked him if he w\u2026", 
    "reply_settings": "everyone", 
    "possibly_sensitive": False, 
    "source": "Twitter for iPhone", 
    "public_metrics": {"retweet_count": 1256, "reply_count": 0, "like_count": 0, "quote_count": 0}, 
    "lang": "en", 
    "referenced_tweets": [{"type": "retweeted", "id": "1353880904188506112", 
        "entities": {"urls": [{"start": 274, "end": 297, "url": "https://t.co/9CovM6hF9P", "expanded_url": "https://twitter.com/tradehunter305/status/1353880904188506112/video/1", "display_url": "pic.twitter.com/9CovM6hF9P"}], "hashtags": [{"start": 228, "end": 243, "tag": "tradehunter305"}, {"start": 244, "end": 256, "tag": "miamifreaks"}], "annotations": [{"start": 134, "end": 141, "probability": 0.5495, "type": "Person", "normalized_text": "Ofocurse"}], "mentions": [{"start": 178, "end": 191, "username": "_BDhandsome1"}, {"start": 257, "end": 273, "username": "tradehunter_305"}]}, 
        "conversation_id": "1353880904188506112", "text": "While checking into my hotel, I seen this light skin dude behind me. We ended up on the same floor, I asked him if he wanted to smoke Ofocurse he agreed. Come to find out it was @_BDhandsome1 I had to eat that pretty dick up \ud83d\udc45\ud83c\udf46 #tradehunter305 #miamifreaks @tradehunter_305 https://t.co/9CovM6hF9P", "reply_settings": "everyone", "possibly_sensitive": true, "source": "Twitter for iPhone", "attachments": {"media_keys": ["7_1353879826868875264"], "media": [{}]}, "public_metrics": {"retweet_count": 1256, "reply_count": 23, "like_count": 4509, "quote_count": 23}, "lang": "en", "created_at": "2021-01-26T01:42:16.000Z", "author_id": "63184818", "geo": {"place_id": "04cb31bae3b3af93"}, "author": {"url": "https://t.co/zsgog6bssy", "name": "Beast", "pinned_tweet_id": "1353880904188506112", "public_metrics": {"followers_count": 33671, "following_count": 360, "tweet_count": 6666, "listed_count": 78}, "location": "Miami, FL", "entities": {"url": {"urls": [{"start": 0, "end": 23, "url": "https://t.co/zsgog6bssy", "expanded_url": "https://onlyfans.com/tradehunter305", "display_url": "onlyfans.com/tradehunter305"}]}}, "id": "63184818", "protected": false, "username": "tradehunter305", "description": "HAITIAN NIGGA \ud83c\udded\ud83c\uddf9 big dick, fat ass, deepthroat. I\u2019m Vtop that love to suck \ud83c\udf46 and fuck \ud83c\udf51. follow back up page tradehunter_305", "verified": false, "profile_image_url": "https://pbs.twimg.com/profile_images/1181809641124237312/RBOiw6OA_normal.jpg", "created_at": "2009-08-05T16:48:42.000Z"}}], 
    "id": "1365618709222600705", 
    "created_at": "2021-02-27T11:04:06.000Z", 
    "author_id": "867867068988874752", 
    "entities": {"mentions": [{"start": 3, "end": 18, "username": "tradehunter305", "url": "https://t.co/zsgog6bssy", "name": "Beast", "pinned_tweet_id": "1353880904188506112", "public_metrics": {"followers_count": 33671, "following_count": 360, "tweet_count": 6666, "listed_count": 78}, "location": "Miami, FL", "entities": {"url": {"urls": [{"start": 0, "end": 23, "url": "https://t.co/zsgog6bssy", "expanded_url": "https://onlyfans.com/tradehunter305", "display_url": "onlyfans.com/tradehunter305"}]}}, "id": "63184818", "protected": false, "description": "HAITIAN NIGGA \ud83c\udded\ud83c\uddf9 big dick, fat ass, deepthroat. I\u2019m Vtop that love to suck \ud83c\udf46 and fuck \ud83c\udf51. follow back up page tradehunter_305", "verified": false, "profile_image_url": "https://pbs.twimg.com/profile_images/1181809641124237312/RBOiw6OA_normal.jpg", "created_at": "2009-08-05T16:48:42.000Z"}]}, "author": {"url": "", "name": "Gooddae", "public_metrics": {"followers_count": 227, "following_count": 1378, "tweet_count": 10233, "listed_count": 1}, "location": "Atlanta, GA", "entities": {"description": {"hashtags": [{"start": 61, "end": 65, "tag": "ATL"}, {"start": 66, "end": 71, "tag": "BEAR"}, {"start": 83, "end": 91, "tag": "JUSTFUN"}]}}, "id": "867867068988874752", "protected": false, "username": "Gooddae80", "description": "Just here for the entertainment and reposting what I like... #ATL #BEAR I guess... #JUSTFUN add my switch code SW-5138-3277-6701", "verified": false, "profile_image_url": "https://pbs.twimg.com/profile_images/1208330683371937792/mTfONoQU_normal.jpg", "created_at": "2017-05-25T22:16:48.000Z"}}
tweet.get("conversation_id")


# Opening twarc stuff
with open('/work/50114/twitter/twarc_test.json') as json_file:
    twarc = json.load(json_file)


with open('/work/50114/twitter/twarc_flatter.ndjson') as json_file:
    twarcs = ndjson.load(json_file)

for line in twarcs: 
    print(line["text"])