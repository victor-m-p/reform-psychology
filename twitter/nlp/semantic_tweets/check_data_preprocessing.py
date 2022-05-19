
# imports 
import pandas as pd
import numpy as np
import pickle 
import re 
import argparse 
from pathlib import Path
pd.set_option('mode.chained_assignment', None) # suppresses and turn off the warning
dd

''' convenience function '''
def get_weighted(df, cols): 
    '''
    df: <pd.dataframe> 
    cols: <list> list of column-names
    '''
    df = df.groupby(cols).size().reset_index(name = 'weight')
    return df 

## first concat them 
def gather_tweet_types(df_lst, group_cols, remove_self_reference = True):
    '''
    df_lst: <list> list of dataframes 
    group_cols: <list> list of column names to group by 
    remove_self: <bool> whether to remove self-links 
    '''
    
    df_main = pd.concat(df_lst) # concat dfs
    df_total = df_main.groupby(group_cols)['weight'].sum().reset_index(name = 'weight') # weight
    df_total = df_total.dropna() # remove na 
    if remove_self_reference: # remove self-reference
        df_total = df_total[df_total["username_from"] != df_total["username_to"]]
    return df_total

# read stuff
infile = "/work/50114/twitter/data/nlp/subsets/os_rc_5.pickle"
with open(f"{infile}", "rb") as f:
    dct = pickle.load(f)
df_semantic = pd.DataFrame.from_dict(dct)

# check it 
len(df_semantic['main_author_username'].unique()) # 989 unique accounts -- this is what we should backbone
df_semantic_authors = df_semantic[["main_author_username"]]
df_semantic_authors = df_semantic_authors.rename(columns = {'main_author_username': 'username'})
df_semantic_authors = df_semantic_authors.drop_duplicates()

# setup # 
remove_self_reference = True
infile_openscience = "/work/50114/twitter/data/raw/preprocessed/openscience.pickle"
infile_repcrisis = "/work/50114/twitter/data/raw/preprocessed/replicationcrisis.pickle"

###### step 1: preparation #######
## read data & get filename
def read_data(infile):
    with open(f"{infile}", "rb") as f:
        dct = pickle.load(f)
    df = pd.DataFrame.from_dict(dct)
    return df 

df_open = read_data(infile_openscience)
df_rep = read_data(infile_repcrisis)

len(df_open) # 2.003.614
len(df_rep) # 76.515

## subset columns & rename 
def subset_cols(df): 
    subset_cols = ["main_author_username", "ref_author_username", "main_text", "type_tweet"]
    df = df[subset_cols]
    df = df.rename(columns = {
        'main_author_username': 'username_from',
        'ref_author_username': 'username_to'
    })
    return df

df_open_sub = subset_cols(df_open)
df_rep_sub = subset_cols(df_rep)

###### intermezzo ###### 
## check that we actually have the data here ## 
def edgelist_to_authors(d, from_col, to_col):
    df_src_authors = d[[from_col]]
    df_trg_authors = d[[to_col]].rename(columns = {to_col: from_col})
    df_concat_authors = pd.concat([df_src_authors, df_trg_authors])
    df_authors_edgelist = df_concat_authors.drop_duplicates()
    df_authors_edgelist = df_authors_edgelist.rename(columns = {from_col: 'username'})
    print(len(df_authors_edgelist)) 
    return df_authors_edgelist

d_total = pd.concat([df_open_sub, df_rep_sub])
d_total_edgelist = edgelist_to_authors(d_total, "username_from", "username_to")
d_combined = d_total_edgelist.merge(df_semantic_authors, on = "username", how = "inner")
len(d_combined) # 978 (all there)
len(df_semantic_authors) # 978 (all there)

###### step 2: in steps ######
# clean tweet types individually: 
group_cols = ['username_from', 'username_to']

## (1) quoted --> originals
def get_quoted(d, group_cols): 
    d = d[d["type_tweet"] == "quoted"]
    d = get_weighted(d, group_cols)
    return d

df_open_quoted = get_quoted(df_open_sub, group_cols)
df_rep_quoted = get_quoted(df_rep_sub, group_cols)

## (2) RT --> original 
def get_retweeted(d, group_cols):
    d = d[d["type_tweet"] == "retweeted"]
    d = get_weighted(d, group_cols)
    return d

df_open_retweet = get_retweeted(df_open_sub, group_cols)
df_rep_retweet = get_retweeted(df_rep_sub, group_cols)

## (3) replied --> original + other
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

df_open_replied = get_replied(df_open_sub, group_cols)
df_rep_replied = get_replied(df_rep_sub, group_cols)

## (4) gather everything
df_open_lst = [df_open_quoted, df_open_retweet, df_open_replied]
df_open_clean = gather_tweet_types(df_open_lst, group_cols, remove_self_reference)

df_rep_lst = [df_rep_quoted, df_rep_retweet, df_rep_replied]
df_rep_clean = gather_tweet_types(df_rep_lst, group_cols, remove_self_reference)

##### put the two together ######
df_rep_clean["from"] = "replication"
df_open_clean["from"] = "openscience"
len(df_rep_clean) # 68.185
len(df_open_clean) # 1.071.097
df_total = pd.concat([df_rep_clean, df_open_clean])
len(df_total) # 1.139.282

##### check whether this is the same as before (not the same) #####
df_rep_previous = pd.read_csv("/work/50114/twitter/data/network/preprocessed/replicationcrisis_edgelist_simple.csv")
df_open_previous = pd.read_csv("/work/50114/twitter/data/network/preprocessed/openscience_edgelist_simple.csv")
len(df_rep_previous) # 52.742
len(df_open_previous) # 951.216

##### check whether we now have everything #####
df_total_authors = edgelist_to_authors(df_total, "username_to", "username_from")
df_semantic_authors.head(5)
df_combined = df_total_authors.merge(df_semantic_authors, on = "username", how = "inner")
len(df_combined) # 843: we lack them here as well --> and we apparently should as well. 
len(df_semantic_authors) # 978: we have them here. 

### find the accounts that we are lackign ###
semantic_authors = list(df_semantic_authors["username"])
combined_authors = list(df_combined["username"])
missing_authors = list(set(semantic_authors) - set(combined_authors))
missing_authors

# find them in one of the documents #
def find_account(d, account): 
    in_from = d[d["username_from"] == account]
    in_to = d[d["username_to"] == account]
    return in_from, in_to 

#### YES: these have actually posted, but no-one (seamingly) has interacted with these users ####
## --> this sounds crazy, but is actually true --- 
## --> and this highlights the need for the other plot 
## --> because it highlights the actual important players 
## --> also need a plot with "weight" over time (i.e. one tweet has a weight + then we can weight it by number of interactions -- RTs, QTs, REPLY)
## --> it is really crazy, but we have double-checked this actually. 
pd.set_option('display.max_colwidth', None)
in_from, in_to = find_account(df_open_sub, "CorrelViz")
in_from # 2 posts here to None (original post)
in_to # not in to 
in_from, in_to = find_account(df_rep_sub, "CorrelViz")
in_from # many here to None (original post) -- same post ... with different links ... a lot of times 
in_from, in_to = find_account(df_open_sub, "3novices")
in_from # 3 posts to None (original)
in_to # not in to
in_from, in_to = find_account(df_rep_sub, "3novices")
in_from # 2 posts in None (original)
in_to # not in to 
in_from, in_to = find_account(df_open_sub, "NewScientistZon")
in_from # many original posts 
in_to # not in to 
in_from, in_to = find_account(df_rep_sub, "NewScientistZon")
in_from # three posts 
in_to # nothing 

##### check whether it makes most sense to just concat them from get-go -- does this give the same? #####
## create the concatenated data-sat here & then just check it against "df_total" ## 
## if it is the same, then we should definitely use that & just keep this pipeline clean ##
## we can have one document that is just "concatenate the two files" -- ## 
## and then another document that is "get the edgelist" ## 

## pipeline to get the weighted edgelist of the combination ##
group_cols = ["username_from", "username_to"]
df_both = pd.concat([df_open_sub, df_rep_sub])
df_both_quoted = get_quoted(df_both, group_cols)
df_both_retweeted = get_retweeted(df_both, group_cols)
df_both_replied = get_replied(df_both, group_cols)
df_both_lst = [df_both_quoted, df_both_retweeted, df_both_replied]
df_both_clean = gather_tweet_types(df_both_lst, group_cols, remove_self_reference)
len(df_both_clean) # 1.133.870 (a little bit less) but should be more-or-less the same 

## pipeline to get the authors - i.e. openscience, replicationcrisis, overlap ##
df_open_authors = edgelist_to_authors(df_open_sub, "username_from", "username_to")
df_rep_authors = edgelist_to_authors(df_rep_sub, "username_from", "username_to")

df_open_authors["query"] = "openscience"
df_rep_authors["query"] = "replicationcrisis"

authors_overlap = df_open_authors.merge(df_rep_authors, on = "username", how = "outer")

def clean_author(d, query_x, query_y): 
    conditions = [
        (d["query_x"] == query_x) & (d["query_y"].isnull()),
        (d["query_x"].isnull()) & (d["query_y"] == query_y)
        ]
    choices = [query_x, query_y]
    d["query"] = np.select(conditions, choices, default = "overlap")
    d = d.drop(columns = {'query_x', 'query_y'})
    return d 

authors_overlap_clean = clean_author(authors_overlap, "openscience", "replicationcrisis")


