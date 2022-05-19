'''
VMP 2022-05-03
'''

# imports 
import pandas as pd
import numpy as np
import pickle 
import re 
import argparse 
from pathlib import Path
pd.set_option('mode.chained_assignment', None)

''' convenience functions '''
def get_weighted(df, cols): 
    '''
    df: <pd.dataframe> 
    cols: <list> list of column-names
    '''
    df = df.groupby(cols).size().reset_index(name = 'weight')
    return df 

def gather_tweet_types(df_lst, group_cols, remove_self_reference = True):
    '''
    df_lst: <list> list of dataframes 
    group_cols: <list> list of column names to group by 
    remove_self: <bool> whether to remove self-links 
    '''
    
    df_main = pd.concat(df_lst) # concat
    df_total = df_main.groupby(group_cols)['weight'].sum().reset_index(name = 'weight') # weight
    df_total = df_total.dropna() # remove na 
    if remove_self_reference: # remove self-reference
        df_total = df_total[df_total["username_from"] != df_total["username_to"]]
    return df_total

def get_quoted(d, group_cols): 
    d = d[d["type_tweet"] == "quoted"]
    d = get_weighted(d, group_cols)
    return d

def get_retweeted(d, group_cols):
    d = d[d["type_tweet"] == "retweeted"]
    d = get_weighted(d, group_cols)
    return d

def get_replied(d, group_cols): 
    reply_regex = "(@\w+) "
    d = d[d["type_tweet"] == "replied_to"]
    d["mention"] = ["|".join(re.findall(reply_regex, x)).replace('@', '') for x in d["main_text"]]
    d["username_to"] = d["username_to"].fillna('NA') # fill None
    d["mention"] = ["NA" if x == "" else x for x in d["mention"]] # fill empty
    d = d.assign(username_to = lambda x: x["username_to"] + "|" + x["mention"]) # combine
    d = d.assign(username_to = lambda x: x["username_to"].str.split("|")) # separate
    d = d.explode('username_to') # explode
    d = d[d["username_from"] != d["username_to"]] # remove self-loops
    d = d.drop_duplicates() # remove duplicates
    d = d[d["username_from"] != "NA"] # remove NA
    d = get_weighted(d, group_cols)
    return d

# setup 
remove_self_reference = True

# read stuff
infile = "/work/50114/twitter/data/nlp/subsets/os_rc_overlap_concat.pickle"
with open(f"{infile}", "rb") as f:
    dct = pickle.load(f)
df_both = pd.DataFrame.from_dict(dct)
df_both = df_both.dropna()

# run 
group_cols = ["username_from", "username_to"]
df_both_quoted = get_quoted(df_both, group_cols)
df_both_retweeted = get_retweeted(df_both, group_cols)
df_both_replied = get_replied(df_both, group_cols)
df_both_lst = [df_both_quoted, df_both_retweeted, df_both_replied]
df_both_clean = gather_tweet_types(df_both_lst, group_cols, remove_self_reference)
len(df_both_clean) # 1.133.870 (a little bit less) but should be more-or-less the same 

# save (keep in pickle format because there is some deprecation)
outpath = "/work/50114/twitter/data/nlp/edgelists"
filename = "os_rc_edgelist_overlap" 
with open(f'{outpath}/{filename}.pickle', 'wb') as handle:
    pickle.dump(df_both_clean, handle, protocol=pickle.HIGHEST_PROTOCOL)

#df_both_clean.to_csv("/work/50114/twitter/data/nlp/edgelists/os_rc_edgelist_overlap.csv", index = False)