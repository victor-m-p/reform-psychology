'''
VMP 2022-04-26
STEP 1
'''

# imports
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from community import community_louvain
pd.set_option('display.max_colwidth', None)

# read data
d = pd.read_csv("/work/50114/twitter/data/nlp/msg/semantic_topics/os_rc_5_typeretweet_k100_semantic_edgelist.csv")

# symmetric matrix (so clean this)
d = d[d["src"] < d["trg"]]
d["weight"] = [1-x for x in d["dist"]]

# save 
d.to_csv("/work/50114/twitter/data/nlp/msg/network_topics/os_rc_5_typeretweet_k100.csv", index = False)