'''
VMP 2022-04-18: 
Only the intersection of Open Science & Replication Crisis (perhaps incl. all of replication crisis). 
Every handle/author has to have at least two original posts in each domain. 
'''

# setup
import pandas as pd 
import numpy as np 
import pickle 

# read original data 
repcrisis = "/work/50114/twitter/data/raw/preprocessed/replicationcrisis.pickle"
opensci = "/work/50114/twitter/data/raw/preprocessed/openscience.pickle"

with open(f"{repcrisis}", "rb") as f:
    dct_repcrisis = pickle.load(f)

with open(f"{opensci}", "rb") as f: 
    dct_opensci = pickle.load(f)

# convert to dataframe
d_repcrisis = pd.DataFrame.from_dict(dct_repcrisis)
d_opensci = pd.DataFrame.from_dict(dct_opensci)

# has to be original (becomes too small I think)
d_rep_orig = d_repcrisis[d_repcrisis["type_tweet"] == "original"]
d_open_orig = d_opensci[d_opensci["type_tweet"] == "original"]

# has to have more than two original posts: this works really well #
## group it 
cutoff = 2
d_rep_orig_group = d_rep_orig.groupby('main_author_username').size().reset_index(name = 'count').sort_values('count', ascending = False) 
d_open_orig_group = d_open_orig.groupby('main_author_username').size().reset_index(name = 'count').sort_values('count', ascending = False)

## take it out
d_rep_orig_five = d_rep_orig_group[d_rep_orig_group["count"] >= cutoff]
d_open_orig_five = d_open_orig_group[d_open_orig_group["count"] >= cutoff]

d_rep_orig_authors = d_rep_orig[["main_author_username"]].drop_duplicates()
d_open_orig_authors = d_open_orig[["main_author_username"]].drop_duplicates()

d_intersection_orig_five = d_rep_orig_five.merge(d_open_orig_five, on = "main_author_username", how = "inner")
len(d_intersection_orig_five) # 978 total accounts that we are tracking 

## merge back in 
d_rep_orig_five = d_repcrisis.merge(d_intersection_orig_five, on = "main_author_username", how = "inner")
d_open_orig_five = d_opensci.merge(d_intersection_orig_five, on = "main_author_username", how = "inner")
d_total_five = pd.concat([d_rep_orig_five, d_open_orig_five]) ### what we actually use ###

## only non-retweet
d_total_five_rt = d_total_five[d_total_five["type_tweet"] != "retweeted"]
len(d_total_five_rt) # 64.621 non-retweeted (the number of tweets we are tracking)

d_total_five_orig = d_total_five[d_total_five["type_tweet"] == "original"]
len(d_total_five_orig) # 50.518 original (number of original tweets)

d_total_five_orig_size = d_total_five_orig.groupby('main_author_username').size().reset_index(name = 'count').sort_values('count', ascending=False)
d_total_five_orig_size.head(20)

d_total_five_rt_size = d_total_five_rt.groupby('main_author_username').size().reset_index(name = 'count').sort_values('count', ascending = False)
d_total_five_rt_size.head(40) # oatp = open access tracking project

## only language english
d_total_five_rt_en = d_total_five_rt[d_total_five_rt["main_lang"] == "en"]
len(d_total_five_rt_en) # 59.369K (what we actually use)

#### save ####
d_total_five = d_total_five.reset_index(drop = True)
outpath = "/work/50114/twitter/data/nlp/subsets"
filename = "os_rc_5" # is actually os_rc_2
with open(f'{outpath}/{filename}.pickle', 'wb') as handle:
    pickle.dump(d_total_five, handle, protocol=pickle.HIGHEST_PROTOCOL)

