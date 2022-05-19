'''
VMP 2022-04-26: 
backbone topics
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

## read data
d_cleaned = pd.read_csv("/work/50114/twitter/data/nlp/msg/network_tweets/os_rc_5_typeretweet_k100_topics.csv")
d = pd.read_csv("/work/50114/twitter/data/nlp/msg/network_topics/os_rc_5_typeretweet_k100.csv")
d_cleaned = d_cleaned[(d_cleaned["topic_interest"] != "low") & (d_cleaned["coherence"] != "low")] # removing almost half
d_src = d_cleaned.merge(d, left_on = "topic", right_on = "src", how = "inner").drop(columns = ['topic', 'coherence', 'topic_interest', 'words', 'label'])
d_trg = d_cleaned.merge(d_src, left_on = "topic", right_on = "trg", how = "inner").drop(columns = ["topic", 'coherence', 'topic_interest', 'words', 'label'])

## relabel 
df_renamed = d_trg.rename(columns = {
    'weight': 'nij'
})

## backboning disparity filter (DF)
df_threshold = [0.8]
lst_df = []
random.seed(123)
table_df = backboning.disparity_filter(df_renamed, undirected = True)
for i in df_threshold: 
    print(f"DF threshold: {i}")
    random.seed(123)
    bb_df = backboning.thresholding(table_df, i) 
    print(f"number of edges: {len(bb_df)}")
    lst_df.append(bb_df)


### plot them and inspect to make sure that it is sound ###
G = nx.from_pandas_edgelist(
    bb_df,
    source = "src",
    target = "trg",
    edge_attr = "nij"
)

## community detection
parts = community_louvain.best_partition(G, random_state = 123, weight='nij')

##### save #####
# save both bb and d
lst = []
for key, val in parts.items(): 
    lst.append((key, val))

d_topics = pd.DataFrame(
    lst,
    columns = ["topic", "community"]
    )

d_topics.to_csv("/work/50114/twitter/data/nlp/msg/network_topics/os_rc_5_typeretweet_k100_community_df0.8.csv", index = False)
bb_df.to_csv("/work/50114/twitter/data/nlp/msg/network_topics/os_rc_5_typeretweet_k100_backbone_df0.8.csv", index = False)

### manual check ###
from collections import defaultdict
d = defaultdict(list)
for key, val in parts.items():
    d[val].append(key)

pd.set_option('display.max_colwidth', None)

####### df = 0.8 ######
### topic 0 (Publication)
d_cleaned[d_cleaned["topic"] == 2] # peer review
d_cleaned[d_cleaned["topic"] == 4] # paper write
d_cleaned[d_cleaned["topic"] == 17] # knowledge, decolonization
d_cleaned[d_cleaned["topic"] == 32] # scientific, publication
d_cleaned[d_cleaned["topic"] == 36] # openaccess
d_cleaned[d_cleaned["topic"] == 42] # osf 
d_cleaned[d_cleaned["topic"] == 48] # publish
d_cleaned[d_cleaned["topic"] == 53] # impact factor
d_cleaned[d_cleaned["topic"] == 60] # article
d_cleaned[d_cleaned["topic"] == 64] # publishing, platform
d_cleaned[d_cleaned["topic"] == 82] # journal, editor
d_cleaned[d_cleaned["topic"] == 83] # preprint, service
d_cleaned[d_cleaned["topic"] == 90] # society, royal, launch
d_cleaned[d_cleaned["topic"] == 93] # access, publisher 

### topic 1 (Training & Culture)
d_cleaned[d_cleaned["topic"] == 0] # public, trust
d_cleaned[d_cleaned["topic"] == 7] # scientist, trust
d_cleaned[d_cleaned["topic"] == 16] # practice, qrp
d_cleaned[d_cleaned["topic"] == 20] # change culture
d_cleaned[d_cleaned["topic"] == 37] # training, book, course
d_cleaned[d_cleaned["topic"] == 39] # transparency, accessibility
d_cleaned[d_cleaned["topic"] == 3] # initiative, openness
d_cleaned[d_cleaned["topic"] == 43] # researcher, career
d_cleaned[d_cleaned["topic"] == 41] # community, member
d_cleaned[d_cleaned["topic"] == 46] # research, reproducible
d_cleaned[d_cleaned["topic"] == 71] # support, library, infrastructure
d_cleaned[d_cleaned["topic"] == 89] # coalition, incentive, infrastructure

### topic 3 (Reform Psychology Core)
d_cleaned[d_cleaned["topic"] == 13] # transparency, openness, incentives
d_cleaned[d_cleaned["topic"] == 5] # social psych
d_cleaned[d_cleaned["topic"] == 34] # reproducibility, openness, replicability, nosek
d_cleaned[d_cleaned["topic"] == 35] # psychology, theory, prereg
d_cleaned[d_cleaned["topic"] == 1] # preregistration, decade, low power, method, model
d_cleaned[d_cleaned["topic"] == 70] # psychology, debate, crisis
d_cleaned[d_cleaned["topic"] == 75] # crisis, replication, statistical, theory, measurement
d_cleaned[d_cleaned["topic"] == 94] # study, replicate, prereg
d_cleaned[d_cleaned["topic"] == 95] # future, communication, 
d_cleaned[d_cleaned["topic"] == 99] # conference, osc

### topic 2 (Data & Policy)
d_cleaned[d_cleaned["topic"] == 14] # eu, elsevi
d_cleaned[d_cleaned["topic"] == 21] # share, code, data
d_cleaned[d_cleaned["topic"] == 6] # health, data
d_cleaned[d_cleaned["topic"] == 40] # innovation, tech, citizen
d_cleaned[d_cleaned["topic"] == 50] # policy, platform
d_cleaned[d_cleaned["topic"] == 56] # report, register, prereg
d_cleaned[d_cleaned["topic"] == 59] # datascience, ai, iot
d_cleaned[d_cleaned["topic"] == 65] # datum, management, sharing, available
d_cleaned[d_cleaned["topic"] == 92] # opendata, openresearch

### topic 4 (OSF)
d_cleaned[d_cleaned["topic"] == 38] # free, software
d_cleaned[d_cleaned["topic"] == 28] # framework, osf
d_cleaned[d_cleaned["topic"] == 45] # use, link, osf
d_cleaned[d_cleaned["topic"] == 98] # project, osf
