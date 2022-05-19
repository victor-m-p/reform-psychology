'''
VMP 2022-04-26: 
backbone tweets
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
d_cleaned = pd.read_csv("/work/50114/twitter/data/nlp/msg_network/os_rc_5_typeretweet_k100_topics.csv")
d = pd.read_csv("/work/50114/twitter/data/nlp/msg_network/os_rc_5_typeretweet_k100_prune2.0.csv")
d_cleaned = d_cleaned[(d_cleaned["topic_interest"] != "low") & (d_cleaned["coherence"] != "low")] # removing almost half
d_src = d_cleaned.merge(d, left_on = "topic", right_on = "W_src", how = "inner").drop(columns = ['topic', 'coherence', 'topic_interest', 'words', 'label'])
d_trg = d_cleaned.merge(d_src, left_on = "topic", right_on = "W_trg", how = "inner").drop(columns = ["topic", 'coherence', 'topic_interest', 'words', 'label'])

## relabel 
df_renamed = d_trg.rename(columns = {
    'W_src': 'src',
    'W_trg': 'trg',
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

d_topics.to_csv("/work/50114/twitter/data/nlp/msg_network/os_rc_5_typeretweet_k100_community_df0.8.csv", index = False)
bb_df.to_csv("/work/50114/twitter/data/nlp/msg_network/os_rc_5_typeretweet_k100_backbone_df0.8.csv", index = False)

### manual check ###
from collections import defaultdict
d = defaultdict(list)
for key, val in parts.items():
    d[val].append(key)

##### df = 0.85 #####
pd.set_option('display.max_colwidth', None)

####### df = 0.8 ######
### topic 1 (presentation, learning, student)
d_cleaned[d_cleaned["topic"] == 0] # public, trust, health
d_cleaned[d_cleaned["topic"] == 1] # learn, preregistration, power, decade, method
d_cleaned[d_cleaned["topic"] == 7] # scientist, trust, badge
d_cleaned[d_cleaned["topic"] == 38] # free, software, source, course
d_cleaned[d_cleaned["topic"] == 28] # framework, osf, webinar
d_cleaned[d_cleaned["topic"] == 37] # training, handbook
d_cleaned[d_cleaned["topic"] == 45] # osf, student, presentation
d_cleaned[d_cleaned["topic"] == 97] # edtech, sciencematter, scicomm
d_cleaned[d_cleaned["topic"] == 98] # project, fund, lab, osf, student
d_cleaned[d_cleaned["topic"] == 99] # conference, osc, presentation

### topic 3 (publication, preprint, peer review, osf)
d_cleaned[d_cleaned["topic"] == 2] # review, peer
d_cleaned[d_cleaned["topic"] == 3] # initative, review, openness
d_cleaned[d_cleaned["topic"] == 4] # paper, write, code, available
d_cleaned[d_cleaned["topic"] == 41] # communnity building
d_cleaned[d_cleaned["topic"] == 42] # center, launch, osf, nosek
d_cleaned[d_cleaned["topic"] == 71] # support, infrastructure
d_cleaned[d_cleaned["topic"] == 83] # preprint, server

### topic 0 (reproducibility, preregistration, incentive structure, openness, integrity)
d_cleaned[d_cleaned["topic"] == 13] # transparency, openness, incentive, integrity
d_cleaned[d_cleaned["topic"] == 16] # practice, principle, questionable
d_cleaned[d_cleaned["topic"] == 20] # change, culture, incentive
d_cleaned[d_cleaned["topic"] == 34] # reproducibility, openness, improve, replicability
d_cleaned[d_cleaned["topic"] == 46] # research, reproducibility, integrity
d_cleaned[d_cleaned["topic"] == 39] # available, accessible, transparent, reproducible
d_cleaned[d_cleaned["topic"] == 56] # report, register, registered, preregistration

### topic 5 (psychology, replication crisis, preregistration, theory, statistics)
d_cleaned[d_cleaned["topic"] == 5] # social, medium, psych
d_cleaned[d_cleaned["topic"] == 35] # psychology, bad theory, preregistration, nosek
d_cleaned[d_cleaned["topic"] == 75] # crisis, replication, statistical
d_cleaned[d_cleaned["topic"] == 70] # psychologys, debate, crisis, silver lining
d_cleaned[d_cleaned["topic"] == 94] # study, replicate, fail, replication, preregister
d_cleaned[d_cleaned["topic"] == 95] # future, communication, crisis, vision

### topic 4 (datascience, technology, innovation, open access)
d_cleaned[d_cleaned["topic"] == 21] # share, code, data
d_cleaned[d_cleaned["topic"] == 17] # knowledge, decolonization
d_cleaned[d_cleaned["topic"] == 32] # scientific, information, publication
d_cleaned[d_cleaned["topic"] == 6] # health, data
d_cleaned[d_cleaned["topic"] == 14] # europe, elsevi
d_cleaned[d_cleaned["topic"] == 40] # innovation, tech
d_cleaned[d_cleaned["topic"] == 36] # openaccess, openresearch
d_cleaned[d_cleaned["topic"] == 43] # career
d_cleaned[d_cleaned["topic"] == 50] # policy, platform
d_cleaned[d_cleaned["topic"] == 59] # datascience
d_cleaned[d_cleaned["topic"] == 64] # publishing, platform
d_cleaned[d_cleaned["topic"] == 65] # datum, management, analysis, version
d_cleaned[d_cleaned["topic"] == 92] # opendata, openresearch
d_cleaned[d_cleaned["topic"] == 93] # access, publisher, source

### topic 2 (publication, publish/perish, impact factor, badge)
d_cleaned[d_cleaned["topic"] == 48] # publish, result, perish
d_cleaned[d_cleaned["topic"] == 53] # impact factor
d_cleaned[d_cleaned["topic"] == 60] # article, badge
d_cleaned[d_cleaned["topic"] == 78] # case, replicationcrisis, method, publication, badge
d_cleaned[d_cleaned["topic"] == 82] # journal, editor, badge
d_cleaned[d_cleaned["topic"] == 90] # royal society, launch, submission