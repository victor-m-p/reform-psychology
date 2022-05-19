'''
VMP 2022-04-18: 
Only the overlap of Open Science & Replication Crisis (perhaps incl. all of replication crisis). 
Just concatenates the two documents
'''

import pandas as pd 
import pickle
import numpy as np

### step 1: preparation ###
infile_openscience = "/work/50114/twitter/data/raw/preprocessed/openscience.pickle"
infile_repcrisis = "/work/50114/twitter/data/raw/preprocessed/replicationcrisis.pickle"

## read data & get filename
def read_data(infile):
    with open(f"{infile}", "rb") as f:
        dct = pickle.load(f)
    df = pd.DataFrame.from_dict(dct)
    return df 

df_open = read_data(infile_openscience)
df_rep = read_data(infile_repcrisis)

## subset columns 
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

## concat and save 
df_both = pd.concat([df_open_sub, df_rep_sub])
outpath = "/work/50114/twitter/data/nlp/subsets"
filename = "os_rc_overlap_concat" # is actually os_rc_2
with open(f'{outpath}/{filename}.pickle', 'wb') as handle:
    pickle.dump(df_both, handle, protocol=pickle.HIGHEST_PROTOCOL)

### step 2: unique authors ###
def edgelist_to_authors(d, from_col, to_col):
    df_src_authors = d[[from_col]]
    df_trg_authors = d[[to_col]].rename(columns = {to_col: from_col})
    df_concat_authors = pd.concat([df_src_authors, df_trg_authors])
    df_authors_edgelist = df_concat_authors.drop_duplicates()
    df_authors_edgelist = df_authors_edgelist.rename(columns = {from_col: 'username'})
    print(len(df_authors_edgelist)) 
    return df_authors_edgelist

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

## save 
#authors_overlap_clean.to_csv("/work/50114/twitter/data/nlp/subsets/os_rc_overlap_authors.csv", index = False)
outpath = "/work/50114/twitter/data/nlp/subsets"
filename = "os_rc_overlap_authors" # is actually os_rc_2
with open(f'{outpath}/{filename}.pickle', 'wb') as handle:
    pickle.dump(authors_overlap, handle, protocol=pickle.HIGHEST_PROTOCOL)