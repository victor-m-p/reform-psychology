import pandas as pd 
import numpy as np
import re

tweets = pd.read_csv("/work/50114/twitter/data/csv/tweet/openscience_tweet.csv")

''' check tweets '''
len(tweets) # 21K
len(tweets.drop_duplicates()) # 21K
tweets.head(5)

''' check columns '''
tweets.dtypes

''' check tweet type '''
tweets.tweet_type.unique() # 'retweeted', 'quoted', 'original', 'replied_to' 
tweets.groupby('tweet_type').size().head() # retweet by far most popular. 
replied_to = tweets[tweets["tweet_type"] == "replied_to"]
original = tweets[tweets["tweet_type"] == "original"]
original.head(5)
replied_to.head(5) # should be text here I think. 
original.head(5)
'''
original: 
* has mentionees. 

replied_to: 
* has mentionees
'''

''' for retweets and quotes find the original '''
tweet_author = tweets[["tweet_id", "author_id"]].drop_duplicates()
tweet_author = tweet_author.rename(columns={'tweet_id': 'tweet_id_original', 'author_id': 'author_id_original'})
tweet_w_orig = tweets.merge(tweet_author, on = 'tweet_id_original', how = 'left')
len(tweet_w_orig) # not quite as much data now. ---only those that refer to people that also post in our set. 
tweet_w_orig.head(5) # looks fine. 

''' explode stuff '''
# https://medium.com/analytics-vidhya/pandas-explode-b162e7a85d3f
df_exp=tweet_w_orig.assign(mentionees=tweet_w_orig['mentionees'].str.split('|')).explode('mentionees')
replied_to = df_exp[df_exp["tweet_type"] == "replied_to"]
len(df_exp) # a bit longer 

''' add mentionees author_id '''