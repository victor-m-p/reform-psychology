'''
VMP 2022-03-03: manual checks.
manually checks tweets to be sure of the information in various columns
'''

import pandas as pd
import numpy as np
import pickle 
import re
pd.set_option('display.max_colwidth', None)

# read pickle 
with open("/work/50114/twitter/data/raw/preprocessed/bropenscience.pickle", "rb") as f:
    dct = pickle.load(f)

''' create pandas dataframe '''
## works: now ids kept as strings. 
df = pd.DataFrame.from_dict(dct)

''' check replies '''
def check_replies(df, type):
    # how much data is there total
    total_rows = len(df)

    # subset frames
    df_reply = df[df["reply_author_id"] != "None"]
    df_noreply = df[df["reply_author_id"] == "None"]

    # how many start with @
    total_reply = len(df_reply)
    total_noreply = len(df_noreply)
    mention_reply = len(df_reply[df_reply["main_text"].str.startswith('@')]) 
    mention_noreply = len(df_noreply[df_noreply["main_text"].str.startswith('@')]) 

    # print 
    print(f"\n--- check replies ({type}) ---")
    print(f"total rows: {total_rows}")
    print(f"number reply: {total_reply}")
    print(f"number noreply: {total_noreply}")
    print(f"number reply (starts with @): {mention_reply}")
    print(f"number no-reply (starts with @): {mention_noreply}")

    # return 
    return df_reply, df_noreply 


''' check stuff (for each tweet type) '''
df_original = df[df["type_tweet"] == "original"]
df_quoted = df[df["type_tweet"] == "quoted"]
df_reply = df[df["type_tweet"] == "replied_to"]
df_retweet = df[df["type_tweet"] == "retweeted"]

''' check truncation '''
df_original["main_text"].head(5) # not truncated
df_quoted["main_text"].head(5) # not truncated
df_reply["main_text"].head(5) # not truncated
df_retweet["main_text"].head(5) # is truncated

''' original '''
## overall take ## 
# (a) "reply_author_id" can happen when original tweets start with @
# (b) "ref_author_username" never happens. 
# (c) "mentions" happens in < 50% but when they do they are ok. 

# (1) reply_author_id: 
cols = ["main_text", "reply_author_id"]

## (1.1) happens rarely: 
df_original_reply, df_original_noreply = check_replies(df_original, "original")

## (1.2) manual check
df_original_reply[cols].head(5)
df_original_noreply[cols].head(5)

# (2) reference_tweet_id (never): 
df_original.groupby('ref_author_username').size()

# (3) mentions: 
cols = ["main_text", "main_mentions_username"]
## (3.1) most often not, but sometimes - seems to work. 
df_original.groupby('main_mentions_username').size().reset_index(name = 'count').sort_values('count', ascending=False)
df_original[cols].head(5)

''' quoted '''
## overall take ##
# (a) "reply_author_id": a bit weird that it does not always start with @
# (b) "ref_author_username": always there, and what we actually care about (the one they QUOTE)
# (c1) "main_mentions_username": mentions in the quote tweet.
# (c2) "ref_mentions_username": mentions in the tweet that is quoted.
# (c3) "mentions_total_username": both of the above. 
# (d) "ref_text": text of the tweet that is quoted. 
# so we can use (b) for main pipeline and (c1, c2 or c3) for extended. 
# might want to check how relevant the "ref_text" seems. 

# (1) "reply_author_id": 
cols = ["main_text", "reply_author_id"]

## (1.1) happens some percentage (many reply not start with @)
quote_reply, quote_noreply = check_replies(df_quoted, "quoted")

# (1.2) manual check (not sure yet)
quote_reply[cols].head(5)

# (2) "ref_author_username": always reference (not None) 
df_quoted.groupby('ref_author_username').size().reset_index(name = 'count').sort_values('count', ascending=False).head(5)
len(df_quoted[df_quoted["ref_author_username"] == "None"])

# (2.1) are these the ones they are quoting? (manual check)
# yes, these are the ones that we actually want! 
cols = ["main_text", "main_author_username", "ref_author_username"]
df_quoted[cols].head(5)

# (3) mentions 
cols = ["main_text", "ref_text", "main_mentions_username", "ref_mentions_username", "mentions_total_username"]

## (3.1) in original tweet: many None, but otherwise seems legit
df_quoted.groupby('main_mentions_username').size().reset_index(name = 'count').sort_values('count', ascending=False).head(5)

## (3.1.1) check some manually: looks good. 
df_quoted_main = df_quoted[df_quoted["main_mentions_username"] != "None"]
df_quoted_main[cols].head(5)

## (3.2) in reference tweet: many None, but otherwise good.
df_quoted.groupby('ref_mentions_username').size().reset_index(name = 'count').sort_values('count', ascending=False).head(5)

## (3.2.1) check some manually: looks good.
df_quoted_ref = df_quoted[df_quoted["ref_mentions_username"] != "None"]
df_quoted_ref[cols].head(5)

## (3.3) also works with total mentions (just both).

## (4) how relevant is the original tweets that they reference? (for future)

## (5) how likely are we to have the original tweets that they reference? (for future)

''' retweet '''
## overall take ##
# (a) "reply_author_id": never reply.
# (b) "ref_author_username": always there, and what we actually care about (the one they RT)
# (c) "main_mentions_username" & "mentions_total_username" is the same (just different order)
# --> so we can use (b) for first pipeline and (c) for extended. 

# (1) reply_author_id: 
cols = ["main_text", "reply_author_id"]

## (1.1) never reply. 
retweet_reply, retweet_noreply = check_replies(df_retweet, "retweet")

# (2) "ref_author_username": always reference (not None) 
df_retweet.groupby("ref_author_username").size().reset_index(name = 'count').sort_values('count', ascending=False).head(5)
len(df_retweet[df_retweet["ref_author_username"] == "None"])

# (3) mentions: (specific issue because of truncation: only for RT)
## (3.1) "main_mentions_username": gives the one that it is RT of + their mentions (all @)
df_retweet.groupby('main_mentions_username').size().reset_index(name = 'count').sort_values('count', ascending=False).head(5)

## (3.2) "ref_mentions_username": many None, but also some (probably from the original tweet)
df_retweet.groupby('ref_mentions_username').size().reset_index(name = 'count').sort_values('count', ascending=False).head(5)

## (3.2.1) manual check: 
cols = ["main_text", "ref_text", "ref_mentions_username", "ref_author_username", "main_mentions_username"]
df_retweet_ref = df_retweet[df_retweet["ref_mentions_username"] != "None"]
df_retweet_ref[cols].head(5)

### (3.2.3) checking why / why not the same (mentions_total_username & main_mentions_username)
#### they are the same (just order can be different)
cols = ["main_text", "ref_text", "mentions_total_username", "main_mentions_username"] 
mentions_main_vs_total = df_retweet[(df_retweet["mentions_total_username"] != df_retweet["main_mentions_username"])]
mentions_main_vs_total[cols].head(5)

''' replied_to '''
## overall take ##
# (a) "reply_author_id": always reply (but we do not have username, only id) -- we do not need this.
# (b) "ref_author_username": always there, and what we actually care about (the one they RT)
# (c1) "main_mentions_username": mentions in the RT tweet + in the RT (but could be truncated?)
# --> often the same as mentions_total_username... but not always. 
# (c2) "ref_mentions_username": mentions in the tweet that is RT'ed (good) 
# (c3) "mentions_total_username": both of the above (although could be truncated?)

# (1) reply_author_id: 
cols = ["main_text", "reply_author_id"]

## (1.1) always has "reply_author_id". 
## (1.2) not always starting with @ but > 50%
df_reply_reply, df_reply_noreply = check_replies(df_reply, "reply")

# (2) "ref_author_username": a few None here.
cols = ["main_text", "ref_text", "main_author_username", "ref_author_username", "ref_author_id", "reply_author_id"]
df_reply.groupby("ref_author_username").size().reset_index(name = 'count').sort_values('count', ascending=False).head(5)
len(df_reply[df_reply["ref_author_username"] == "None"])

## (2.1) check the None vs. non-none
df_reply_ref = df_reply[df_reply["ref_author_username"] != "None"]
df_reply_noref = df_reply[df_reply["ref_author_username"] == "None"]

## (2.1.1) check those that do ref
### around half are self-reference
### generally does not start with @
### in these cases, "ref_author_id" == "reply_author_id"
df_reply_ref[cols].head(5)
len(df_reply_ref[df_reply_ref["main_author_username"] == df_reply_ref["ref_author_username"]])
len(df_reply_ref)

## (2.1.2) check those that do not ref 
### generally does start with @ 
### in these cases, we lack "ref_author_id". 
### in these cases we need all @ before main text starts (can be more than one)
### need to compute this myself I think ("reply_author_id" only lists one and we also need username)
### in this case we might not be able to match it to "author name" but we will live with it.
df_reply_noref[cols].head(5)
reply_regex = "(@\w+) "

# this works
df_reply_noref["actual_replied_to"] = ["|".join(re.findall(reply_regex, x)).replace('@', '') for x in df_reply_noref["main_text"]]
df_reply_noref[["main_text", "actual_replied_to"]].head(5)

# (3) mentions 