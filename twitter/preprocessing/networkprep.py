import pandas as pd 
import numpy as np
import re

tweets = pd.read_csv("/work/50114/twitter/data/csv/tweet/openscience_tweet.csv")
users = pd.read_csv("/work/50114/twitter/data/csv/user/openscience_user.csv")

# string seems more safe. 
tweets["tweet_id"] = tweets["tweet_id"].astype('str')
tweets["author_id"] = tweets["author_id"].astype('str')
tweets["tweet_id_original"] = tweets["tweet_id_original"].astype('str')
tweets["in_reply_to"] = tweets["in_reply_to"].astype('str')
users["username"] = users["username"].astype('str')
users["author_id"] = users["author_id"].astype('str')

''' for retweets and quotes find the original '''
tweet_author = tweets[["tweet_id", "author_id"]].drop_duplicates()
tweet_author = tweet_author.rename(columns={'tweet_id': 'tweet_id_original', 'author_id': 'author_id_original'})
tweet_w_orig = tweets.merge(tweet_author, on = 'tweet_id_original', how = 'left')
len(tweet_w_orig) # not quite as much data now. ---only those that refer to people that also post in our set. 
tweet_w_orig.head(5) # looks fine. 
tweet_w_orig.dtypes

''' explode stuff '''
# https://medium.com/analytics-vidhya/pandas-explode-b162e7a85d3f
df_exp=tweet_w_orig.assign(mentionees=tweet_w_orig['mentionees'].str.split('|')).explode('mentionees')

''' add mentionees author_id '''
user_author = users[["username", "author_id"]].drop_duplicates()
user_author = user_author.rename(columns={'username': 'mentionees', 'author_id': 'mentionee_id'})

df_exp.groupby('mentionees').size().to_frame('count').reset_index().sort_values('count', ascending=False).head(5)
user_author.groupby('mentionees').size().to_frame('count').reset_index().sort_values('count', ascending=False).head(5)

df_total = df_exp.merge(user_author, on = 'mentionees', how = 'left')
df_total.head(5)
len(df_total) 

''' actual partition '''
# should probably be better ways of doing this. 
df_retweet_quote = df_total[df_total["tweet_type"].isin(["retweeted", "quoted"])]
df_original_reply = df_total[df_total["tweet_type"].isin(['original', 'replied_to'])]

# more or less same procedure. 
df_retweet_quote = df_retweet_quote[["author_id", "author_id_original", "tweet_type"]]
df_retweet_quote = df_retweet_quote.rename(columns={'author_id': 'from', 'author_id_original': 'to'})
df_retweet_quote['edge_type'] = 'retweet'

df_original_reply = df_original_reply[["author_id", "mentionee_id", "tweet_type"]]
df_original_reply = df_original_reply.rename(columns={'author_id': 'from', 'mentionee_id': 'to'})
df_original_reply['edge_type'] = 'mention'

# bind them 
df_edgelist = pd.concat([df_retweet_quote, df_original_reply])
df_edgelist.head(5)

# save for now 
df_edgelist.to_csv("/work/50114/twitter/data/csv/network/test.csv", index=False)