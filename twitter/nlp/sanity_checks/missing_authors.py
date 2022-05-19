'''
VMP 2022-05-03: lack of overlap between edgelist & semantic investigated --
the explanation is: 
(1) almost all of them only have original tweets 
(2) the rest have retweeted themselves only
'''

import pandas as pd 
import pickle

# read data
infile = "/work/50114/twitter/data/nlp/edgelists/os_rc_5_edgelist_intersection.pickle"
with open(f"{infile}", "rb") as f:
    dct = pickle.load(f)
df_edgelist = pd.DataFrame.from_dict(dct)
#df_edgelist = pd.read_csv("/work/50114/twitter/data/nlp/edgelists/os_rc_5_edgelist_intersection.csv")
df_mapping = pd.read_csv("/work/50114/twitter/data/nlp/msg/semantic_tweets/os_rc_5_typeretweet_k100_prune2.0_nmf.csv")
df_community = pd.read_csv("/work/50114/twitter/data/nlp/msg/network_topics/os_rc_5_typeretweet_k100_community_df0.8.csv")

# clean mapping 
df_mapping_sub = df_mapping[["username", "W_max", "W_val"]].rename(columns = {'W_max': 'topic'})
df_community_user = df_mapping_sub.merge(df_community, on = "topic", how = 'inner') # only those in used topics 
df_community_weight = df_community_user.groupby(['username', 'community'])['W_val'].sum().reset_index(name = 'sum')
max_idx = df_community_weight.groupby(['username'])['sum'].transform(max) == df_community_weight['sum']
df_community_max = df_community_weight[max_idx]
df_community_max = df_community_max[["username", "community"]]

# find overlap 
def edgelist_to_authors(d, from_col, to_col):
    df_src_authors = d[[from_col]]
    df_trg_authors = d[[to_col]].rename(columns = {to_col: from_col})
    df_concat_authors = pd.concat([df_src_authors, df_trg_authors])
    df_authors_edgelist = df_concat_authors.drop_duplicates()
    df_authors_edgelist = df_authors_edgelist.rename(columns = {from_col: 'username'})
    print(len(df_authors_edgelist)) 
    return df_authors_edgelist

df_edgelist_authors = edgelist_to_authors(df_edgelist, from_col = "username_from", to_col = "username_to")
authors_in_both = df_edgelist_authors.merge(df_community_max, on = "username", how = "inner")
authors_in_edgelist = df_edgelist_authors.merge(df_community_max, on = "username", how = "left")
authors_in_semantic = df_community_max.merge(df_edgelist_authors, on = "username", how = "left")

len(authors_in_both) # 731 (still the same number)
len(authors_in_edgelist) # 13.653
len(authors_in_semantic) # 960 

### try to understand gap between 960 and 731 ###
# thesis: (1) some ONLY original (fine) -- perhaps (2) some NAN? 
# we know that some are definately (1) but maybe some are (2)??

### first -- is everything in the original data (yes) ###
infile = "/work/50114/twitter/data/nlp/subsets/os_rc_5.pickle"
with open(f"{infile}", "rb") as f:
    dct = pickle.load(f)
df_original = pd.DataFrame.from_dict(dct)

def subset_cols(df): 
    subset_cols = ["main_author_username", "ref_author_username", "main_text", "type_tweet"]
    df = df[subset_cols]
    df = df.rename(columns = {
        'main_author_username': 'username_from',
        'ref_author_username': 'username_to'
    })
    return df

df_original = subset_cols(df_original)
df_orig_authors = edgelist_to_authors(df_original, "username_from", "username_to")

in_semantic_and_orig = df_orig_authors.merge(df_community_max, on = "username", how = "inner")
len(in_semantic_and_orig) # 960 (all there) 

### second -- locate the missing ones (looks good) ### 
df_edgelist_authors
df_community_max

edgelist_authors = list(df_edgelist_authors["username"])
semantic_authors = list(df_community_max["username"])
missing_authors = list(set(semantic_authors) - set(edgelist_authors))
missing_authors = pd.DataFrame({'username': missing_authors})

# check from-column
username_from = df_original.merge(missing_authors, left_on = "username_from", right_on = "username", how = "inner")
username_from.groupby('type_tweet').size() ## almost all original tweets
username_from_rt = username_from[username_from["type_tweet"] == "retweeted"]
username_from_rt ## retweets are self-retweets 

# check to-column
username_to = df_original.merge(missing_authors, left_on = "username_to", right_on = "username", how = "inner")
username_to.head(5) ## again, only self-retweets 

