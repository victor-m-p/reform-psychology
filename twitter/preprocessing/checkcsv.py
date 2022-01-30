import pandas as pd 
import numpy as np
import re

users = pd.read_csv("/work/50114/twitter/data/csv/user/openscience_user.csv")
tweets = pd.read_csv("/work/50114/twitter/data/csv/tweet/openscience_tweet.csv")

''' check users '''
len(users) # 290 --- why not the same as 348!!??
len(users.id.unique()) # 259 
len(users.drop_duplicates()) # all same users are same stats. 
users.head(5) 

''' check tweets '''
len(tweets) # 348 -- why not the same as 290!!??
len(tweets.drop_duplicates()) # 348, no duplicates (good). 
tweets.head(5)

''' todo '''
# why not same length? (still do not know, but we have all users)
# move on to cleaning (ask Laura about this actually)
# consider what we actually need (& how early to cut out stuff, storage)
# is username the same as handle? (can probably tell from Laura code)
# ---> then we can use the text to actually do stuff. 

''' try to bind them '''
unique_users = users.drop_duplicates()
combined = tweets.merge(unique_users, left_on = "author_id", right_on = "id", how = "inner")

### do we have all authors?: YES ###
len(tweets) 
len(combined)

### how many observations per time point? ### 
combined['month']=combined['created_at'].str.extract('(\d{4}-\d{2})')
combined.groupby('month').size().to_frame('count').reset_index() # why more for the first? 

rt = combined[combined["retweet"] == "retweeted"]
non_rt = combined[combined["retweet"] != "retweeted"]

len(rt)
len(non_rt)

list(non_rt.text)
list(rt.text)

combined.retweet.unique()