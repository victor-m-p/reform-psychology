import pickle 
import pandas as pd 
import re

infile = "/work/50114/twitter/data/raw/preprocessed/openscience.pickle"

# read data & get filename
with open(f"{infile}", "rb") as f:
    dct = pickle.load(f)

df = pd.DataFrame.from_dict(dct)
outname = re.search("preprocessed/(.*).pickle", infile)[1]

# only original tweets & lang = en
df_orig = df[df["type_tweet"] != "retweeted"]
df_orig = df_orig[df_orig["main_lang"] == "en"]

# subset columns & rename
cols = ["main_tweet_id", "main_author_username", "main_text", "main_tweet_date"]
df_sub = df_orig[cols]
df_sub = df_sub.rename(columns = {
    'main_tweet_id': 'tweet_id',
    'main_author_username': 'username',
    'main_text': 'text',
    'main_tweet_date': 'tweet_date'
    })

len(df_sub)