'''
VMP 2022-04-25: 
some inconsistency in my data that I need to check
'''

import argparse
import os
import numpy as np
from sklearn.metrics import pairwise_distances
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
from community import community_louvain
import matplotlib.pyplot as plt
import pandas as pd
import itertools 
import re
import igraph as ig
import time
from tqdm import tqdm
import gc

### set up stuff ###
infile_csv = "/work/50114/twitter/data/nlp/by_tweet/os_rc_5_typeretweet.csv"
infile_W = "/work/50114/twitter/data/nlp/msg/topic_model/os_rc_5_typeretweet_k100_W.txt"
outpath = "/work/50114/twitter/data/nlp/msg/semantic_tweets/"
textcol = "clean_lemma"
prune = 2.0

print("--- starting: nmf ---")

# load W file
print("--> loading data")
W = np.loadtxt(infile_W)
print(W.shape) # (59352, 100)

print("--> pairwise distances")
D = pairwise_distances(W, metric="cosine")
print(D.shape) # (59352, 59352)

print("--> calculate cond")
#cond = np.mean(D) - prune * np.std(D)
print(f"cond = {cond}")
print("--> insert 0")
#D[D > cond] = 0 # probably smarter (distance, so larger than!)

## still this 
print("--> idxs")
idxs = list()
for (i, d) in enumerate(D):
    if i%1000 == 0: 
        print(i)
    if np.sum(d) == 0.:
        idxs.append(i)
print(f"len idx: {len(idxs)}")

#D = np.delete(D, idxs, axis=0) # this is actually the crazy part
#D = np.delete(D, idxs, axis=1)

## update data
print("--> csv & w max")
data = pd.read_csv(infile_csv)
data = data[~data[textcol].isnull()] # this does change it (59370 --> 59352)
data = data.reset_index(drop = True) # this does change it (59370 --> 59352)
print(f"{len(data)}")
len(data)

## add max latent variable index
print("--> W max")
data["W_max"] = np.argmax(W, axis=1)
data["W_val"] = np.max(W, axis=1)
data.drop(idxs, 0, inplace=True) 

## save data 
print(f"--> writing W max dataframe")
outname = re.search("topic_model/(.*)_W.txt", infile_W)[1]
data.to_csv(f'{outpath}{outname}_pruneNO_nmf.csv', index=False)

## distance
distance = D[D != 0]
len(distance) # shorter than below 
len(data) * len(data) # longer than above
distance = pd.DataFrame(distance, columns = ["dist"]) # pretty fast 
data.tail(5) # 59351
## sources, targets
print("--> sources, targets")
sources, targets = D.nonzero() # fine
max(sources) # 59351
max(targets)
len(sources) # endlessly long
len(targets) # endlessly long

##### load old stuff #####
d_orig = pd.read_csv("/work/50114/twitter/data/nlp/msg/semantic_tweets/os_rc_5_typeretweet_k100_prune2.0_nmf.csv")
d_edge = pd.read_csv("/work/50114/twitter/data/nlp/msg/semantic_tweets/os_rc_5_typeretweet_k100__prune2.0_edgelist.csv")

d_orig.tail(5) # 58928 --- a few hundred short
len(d_orig) # 58928
d_edge["src"].max() # 59351 
d_edge["trg"].max() # 59351
len(d_edge["src"].unique()) # 58928
len(d_edge["trg"].unique()) # 58928

# should not actually mess up the index (but perhaps saving and loading does?)
test_df = pd.DataFrame({
    'a': [1, 2, 3],
    'b': [2, 3, 4]
})
test_df["index"] = test_df.index
test_df.head(5) # and the index is now the actual thing

## edgelist
print("--> df edgelist")
df_edgelist = pd.DataFrame(
    zip(sources.tolist(), targets.tolist()),
    columns = ["src", "trg"])

## concat ---> here we fuck it up actually I think
print("--> concatenate stuff")
df_edgelist = pd.concat([df_edgelist.reset_index(drop=True), distance.reset_index(drop=True)], axis=1) # fast

## save edgeslist 
print("--> write edgelist file")
df_edgelist.to_csv(f"{outpath}{outname}__prune{prune}_edgelist.csv", index = False) # writing 