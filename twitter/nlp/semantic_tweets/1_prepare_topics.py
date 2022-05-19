'''
VMP 2022-04-25: 
STEP 1
Should just be the communtiy detection & then save network ---
then actually visualizing it in another document. 
'''

# imports
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from community import community_louvain
pd.set_option('display.max_colwidth', None)

# based just on count of max topic
d = pd.read_csv("/work/50114/twitter/data/nlp/msg/semantic_tweets/os_rc_5_typeretweet_k100_prune2.0_nmf.csv")
log_topics = "/work/50114/twitter/data/nlp/msg/topic_model/os_rc_5_typeretweet_k100_log.txt"
topics = pd.read_csv(log_topics, sep = ":", header = None, skiprows=2)
topics.columns = topics.columns = ["topic", "words"]
W = np.loadtxt("/work/50114/twitter/data/nlp/msg/topic_model/os_rc_5_typeretweet_k100_W.txt")
d_edgelst = pd.read_csv("/work/50114/twitter/data/nlp/msg/semantic_tweets/os_rc_5_typeretweet_k100__prune2.0_edgelist.csv")

# symmetric matrix - so fix this (also remove self-loops) #
d_edgelst = d_edgelst[d_edgelst["src"] < d_edgelst["trg"]] # remove duplication & self-loops
d_edgelst = d_edgelst.sort_values("dist", ascending=True)

## it is inverse (so we need to get inverse)
# just one minus? #
d_edgelst["weight"] = [1-x for x in d_edgelst["dist"]]

## assign max categories to src and trg
d_src = d.rename(columns = {
    'index': 'src',
    'W_max': 'W_src'
})[['src', 'W_src']]

d_trg = d.rename(columns = {
    'index': 'trg',
    'W_max': 'W_trg'
})[["trg", "W_trg"]]

### merge it (has been checked) ###
d_edgelst_src = d_edgelst.merge(d_src, on = "src", how = "inner")
d_edgelst_trg = d_edgelst_src.merge(d_trg, on = "trg", how = "inner")
d_topics_weight = d_edgelst_trg.groupby(['W_src', 'W_trg'])['weight'].sum().reset_index(name = 'weight')

### remove self-loops and symmetric here again ###
d_topics_weight = d_topics_weight[d_topics_weight["W_src"] < d_topics_weight["W_trg"]]

### should save something here ###
d_topics_weight.to_csv("/work/50114/twitter/data/nlp/msg_network/os_rc_5_typeretweet_k100_prune2.0.csv", index = False)

