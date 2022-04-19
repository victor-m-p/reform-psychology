import argparse
import os
import numpy as np
from sklearn.metrics import pairwise_distances
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt
import pandas as pd
import itertools 

# load stuff
data = pd.read_csv("/work/cn-some/data_msg/diplomat_nmf.csv")
G = nx.read_gml("/work/cn-some/data_msg/diplomat_G.gml", destringizer=int) # takes some time to load

def get_new_G(d, G, groupcol, outname): 

    # calculate weight by W_max
    data_dct = dict(zip(d["graph_id"], d[groupcol]))
    from collections import Counter
    cnt = Counter() 

    ### get communities with weight ### 
    for first, second in G.edges():
        c1 = data_dct.get(first)
        c2 = data_dct.get(second)
        c1, c2 = sorted([c1, c2])
        cnt[(c1, c2)] += 1

    # cleaning w
    df = pd.DataFrame.from_dict(cnt, orient = 'index').reset_index()
    df[["left", "right"]] = pd.DataFrame(df['index'].tolist(), index=df.index)
    df = df.rename(columns={0: 'weight'})
    df = df.drop(columns=['index'])

    ### create graph ###
    G = nx.from_pandas_edgelist(df, "left", "right", ["weight"])
    nx.write_gml(G, f'/work/cn-some/msg/data/{outname}.gml')

get_new_G(data, G, "W_max", "diplomat_wmax")
get_new_G(data, G, "graph_community", "diplomat_community")

