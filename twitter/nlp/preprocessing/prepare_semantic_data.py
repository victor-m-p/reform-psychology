'''
VMP 2022-04-22: 
prepare communities over time by authors
'''

# read stuff (test on bropenscience)
# imports
import numpy as np 
import matplotlib.pyplot as plt 
import networkx as nx 
import pandas as pd 
import pickle
pd.set_option('display.max_colwidth', None)

# what do we need: 
## (1) edgelist (not the backboned one for now...)
infile = "/work/50114/twitter/data/nlp/edgelists/os_rc_5_edgelist_intersection.pickle"
with open(f"{infile}", "rb") as f:
    dct = pickle.load(f)
df_edgelist = pd.DataFrame.from_dict(dct)
## (2) the topics & communities:
df_community = pd.read_csv("/work/50114/twitter/data/nlp/msg/network_topics/os_rc_5_typeretweet_k100_community_df0.8.csv")
## (3) the mapping between author and topic
df_mapping = pd.read_csv("/work/50114/twitter/data/nlp/msg/semantic_tweets/os_rc_5_typeretweet_k100_prune2.0_nmf.csv")

#### 1. prepare edgelist #####
## get unique authors from edgelist & semantic ## 
def edgelist_to_authors(d, from_col, to_col):
    df_src_authors = d[[from_col]]
    df_trg_authors = d[[to_col]].rename(columns = {to_col: from_col})
    df_concat_authors = pd.concat([df_src_authors, df_trg_authors])
    df_authors_edgelist = df_concat_authors.drop_duplicates()
    df_authors_edgelist = df_authors_edgelist.rename(columns = {from_col: 'username'})
    print(len(df_authors_edgelist)) 
    return df_authors_edgelist

authors_semantic = df_mapping[["username"]].drop_duplicates()
authors_edgelist = edgelist_to_authors(df_edgelist, "username_from", "username_to")

## find overlap between edgelist & semantic ##
authors_both = authors_semantic.merge(authors_edgelist, on = "username", how = "inner")
authors_both = authors_both.rename(columns = {'username': 'username_from'})

## inner join this on both username_from and username_to ##
df_edgelist_sub = df_edgelist.merge(authors_both, on = "username_from", how = "inner")
authors_both = authors_both.rename(columns = {'username_from': 'username_to'})
df_edgelist_sub = df_edgelist_sub.merge(authors_both, on = 'username_to', how = 'inner')
len(df_edgelist_sub) # MUCH shorter (42K --> 9K)

## we should write this to a file & then do backboning on this actually ##
outpath = "/work/50114/twitter/data/nlp/semantic_info"
filename = "semantic_edgelist" 
with open(f'{outpath}/{filename}.pickle', 'wb') as handle:
    pickle.dump(df_edgelist_sub, handle, protocol=pickle.HIGHEST_PROTOCOL)

#### 2. node-data ####

# load original file
infile = "/work/50114/twitter/data/nlp/subsets/os_rc_5.pickle"
with open(f"{infile}", "rb") as f:
    dct = pickle.load(f)
df_original = pd.DataFrame.from_dict(dct)

# take out important columns
df_original = df_original[df_original["type_tweet"] != "retweeted"]
df_original = df_original[["main_tweet_id", "main_author_username", "tweet_retweet_count", "author_followers_count"]]
df_original = df_original.rename(columns = {
    'main_tweet_id': 'tweet_id',
    'main_author_username': 'username',
    'tweet_retweet_count': 'retweets',
    'author_followers_count': 'followers'
})

# only keep accounts that are in semantic + edgelist 
authors_both = authors_both.rename(columns = {'username_to': 'username'})
df_both = df_original.merge(authors_both, on = "username", how = "inner")
len(df_original) # 64621 
len(df_both) # 61149 (so it is the small accounts we sort here)

### 2. prepare author centered data ###
## followers
author_followers = df_both.groupby('username')['followers'].mean().reset_index(name = 'followers') 

## number of retweets 
author_retweets = df_both.groupby('username')['retweets'].sum().reset_index(name = 'retweet_sum')

## main topic / community
df_mapping = df_mapping.merge(authors_both, on = "username", how = "inner")
df_mapping_sum = df_mapping.groupby(['username', 'W_max'])['W_val'].sum().reset_index(name = 'topic_weight')
df_mapping_sum = df_mapping_sum.rename(columns = {'W_max': 'topic'})

#### first main topic ####
max_idx = df_mapping_sum.groupby(['username'])['topic_weight'].transform(max) == df_mapping_sum['topic_weight']
df_max_topic = df_mapping_sum[max_idx]

#### then max community ####
df_mapping_sum = df_mapping_sum.rename(columns = {'W_max': 'topic'})
df_mapping_comm = df_mapping_sum.merge(df_community, on = "topic", how = "inner")
df_max_comm = df_mapping_comm.groupby(['username', 'community'])['topic_weight'].sum().reset_index(name = 'comm_weight')
max_comm_idx = df_max_comm.groupby(['username'])['comm_weight'].transform(max) == df_max_comm["comm_weight"]
df_max_comm_clean = df_max_comm[max_comm_idx]

### merge these two together ###
df_topic_comm = df_max_topic.merge(df_max_comm_clean, on = "username", how = "outer").fillna(1000)
df_topic_comm["community"] = [int(x) for x in df_topic_comm["community"]]

## gather and save
author_attributes = author_followers.merge(author_retweets, on = "username", how = "inner")
author_attributes = author_attributes.merge(df_topic_comm, on = "username", how = "inner")

outpath = "/work/50114/twitter/data/nlp/semantic_info"
filename = "author_attributes" 
with open(f'{outpath}/{filename}.pickle', 'wb') as handle:
    pickle.dump(author_attributes, handle, protocol=pickle.HIGHEST_PROTOCOL)

### 3. prepare tweet-centered data ###
# ---- #