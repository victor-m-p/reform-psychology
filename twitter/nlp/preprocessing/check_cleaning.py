'''
VMP 2022-03-07: 
check preprocessing of tweets.
the tweets that we do not have are indeed either: 
# (1) non language = en  
# (2) without any non-stopwords 

NB: 
should probably be deleted at some point. 
'''

# imports
import pandas as pd 
import numpy as np 
import pickle 
pd.set_option('display.max_colwidth', -1)

# read cleaned file & original file 
infile_clean = "/work/50114/twitter/data/nlp/by_tweet/bropenscience_tweet_text.csv"
infile_raw = "/work/50114/twitter/data/raw/preprocessed/bropenscience.pickle"
df_clean = pd.read_csv(infile_clean)
with open(infile_raw, "rb") as f:
    dct_raw = pickle.load(f)
df_raw = pd.DataFrame.from_dict(dct_raw)

# looks really good now
# some things: like (I'm) --> (I m) & (Youre) --> (You re) & (havent) --> (have nt)
df_clean.head(10)
