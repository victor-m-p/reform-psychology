'''
VMP 2022-05-19: check volume at different points in the analysis
'''

import pandas as pd 
import pickle 

# number of records (before preprocessing)
## load files (NB: not psyenv)
repcrisis = "/work/50114/twitter/data/raw/preprocessed/replicationcrisis.pickle"
opensci = "/work/50114/twitter/data/raw/preprocessed/openscience.pickle"

with open(f"{repcrisis}", "rb") as f:
    dct_repcrisis = pickle.load(f)

with open(f"{opensci}", "rb") as f: 
    dct_opensci = pickle.load(f)

## convert to dataframe
d_repcrisis = pd.DataFrame.from_dict(dct_repcrisis)
d_opensci = pd.DataFrame.from_dict(dct_opensci)

## subset columns 
subset_cols = ["type_tweet", "main_author_username", "main_tweet_id"]
d_repcrisis = d_repcrisis[subset_cols]
d_opensci = d_opensci[subset_cols]

## total number of tweets (incl. RT) 
len(d_repcrisis) # 76.515
len(d_opensci) # 2.003.614

## total number of tweets (excl. RT)
len(d_repcrisis[d_repcrisis["type_tweet"] != "retweeted"]) # 34.756
len(d_opensci[d_opensci["type_tweet"] != "retweeted"]) # 618.134

## total number of unique handles 
len(d_opensci["main_author_username"].unique()) # 343.688
len(d_repcrisis["main_author_username"].unique()) # 40.350

# overlap condition (see "volume_overlap" in "EDA" folder)

# overlap (restricted to two original per condition)
## NB: requires psyenv to be activated 
inpath = "/work/50114/twitter/data/nlp/subsets/os_rc_5.pickle"
with open(f"{inpath}", "rb") as f:
    dct_overlap_two = pickle.load(f)
dct_overlap_two = dct_overlap_two[subset_cols]

## total number of tweets (incl. RT)
len(dct_overlap_two) # 118.932

## total number of tweets (excl. RT)
len(dct_overlap_two[dct_overlap_two["type_tweet"] != "retweeted"]) # 64.621

## total number of unique handles
len(dct_overlap_two["main_author_username"].unique()) # 989