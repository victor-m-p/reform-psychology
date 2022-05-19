'''
VMP 2022-04-30: backbone the overlap document

'''

# imports 
import backboning # michele backboning module 
import networkx as nx 
import pandas as pd 
import time
import numpy as np
import argparse 
import random
from pathlib import Path
from community import community_louvain
import pickle 

# read 
#df = pd.read_csv("/work/50114/twitter/data/nlp/edgelists/os_rc_edgelist_overlap.csv")
infile = "/work/50114/twitter/data/nlp/edgelists/os_rc_edgelist_overlap.pickle"
with open(f"{infile}", "rb") as f:
    dct = pickle.load(f)
df = pd.DataFrame.from_dict(dct)
df = df.dropna()

# clean up
df_renamed = df.rename(columns = {
    'username_from': 'src',
    'username_to': 'trg',
    'weight': 'nij'
})

## backboning disparity filter (DF)
df_threshold = [0.985, 0.99, 0.995]
lst_df = []
table_df = backboning.disparity_filter(df_renamed, undirected = False)
for i in df_threshold: 
    print(f"DF threshold: {i}")
    bb_df = backboning.thresholding(table_df, i) 
    print(f"number of edges: {len(bb_df)}")
    lst_df.append(bb_df)

## save 
outpath = "/work/50114/twitter/data/nlp/backboning"
for df, threshold in zip(lst_df, df_threshold): 
    with open(f'{outpath}/os_rc_overlap_bb_df_threshold{threshold}.pickle', 'wb') as handle:
        pickle.dump(df, handle, protocol=pickle.HIGHEST_PROTOCOL)
    #df.to_csv(f"{outpath}/os_rc_overlap_bb_df_threshold{threshold}.csv", index = False)
