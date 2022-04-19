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
data = pd.read_csv("/work/cn-some/data_msg/diplomat_orig_nmf.csv")
G2 = nx.read_gml("/work/cn-some/msg/data/diplomat_orig_community.gml", destringizer=int) # takes some time to load

### add meta-data ### 

# add interpretation (by hand) 
dimensions = {
    'W_max': [x for x in range(15)],
    'interpretation': ['transportation', 'diplomacy', 'exhibition', 'pakistan', 'meeting', 'money', 'economy', 'xi-jinping', 'press-conference', 'foreign-affairs', 'trade', 'business-travel', 'embassy', 'life-betterment', 'COVID']
    }

dimension_df = pd.DataFrame(dimensions)
data = data.merge(dimension_df, "inner", "W_max")

# get some summary data that we care about
retweets = data.groupby('graph_community')['retweet_count'].sum().reset_index()
W = data.groupby('graph_community')['W_max'].agg(lambda x: pd.Series.mode(x)[0]).reset_index() # takes first - there could be bias. 
label = data.groupby('graph_community')['interpretation'].agg(lambda x: pd.Series.mode(x)[0]).reset_index()

# add it to our data 
for i in sorted(G2.nodes()): 
    G2.nodes[retweets.graph_community[i]]['retweets'] = retweets.retweet_count[i]
    G2.nodes[W.graph_community[i]]['W_max'] = W.W_max[i]
    G2.nodes[label.graph_community[i]]['interpretation'] = label.interpretation[i]

# remove self-loops
for edge in G2.edges():
    first, second = edge
    if first == second: 
        G2.remove_edge(*edge)

# edge width
edge_width = nx.get_edge_attributes(G2, 'weight').values() 
# edge alpha?
width = [x for x in edge_width]
max_width = max(width)

# node size & color & label
node_size = nx.get_node_attributes(G2, 'retweets').values()
node_color = nx.get_node_attributes(G2, 'W_max').values()
node_label = nx.get_node_attributes(G2, 'interpretation').values()

max(node_size)
import math
##### without color #######
# inspired by: https://networkx.org/documentation/stable/auto_examples/drawing/plot_chess_masters.html
plt.figure(figsize=(12, 12), facecolor='w', edgecolor='k')
plt.axis("off")
pos = nx.spring_layout(G2, seed=7) # can be tweaked individually. 
nx.draw_networkx_nodes(G2, pos, node_size = [x/math.log(x+1) for x in node_size], node_color = list(node_color))
nx.draw_networkx_edges(G2, pos, edge_color = "m", width = [x/2 for x in edge_width], alpha = [x/max_width for x in edge_width])
label_options = {"ec": "k", "fc": "white", "alpha": 0.7}
#nx.draw_networkx_labels(G2,pos,labels=labeldict,font_size=14, bbox=label_options)
plt.tight_layout()
#plt.savefig("/work/cn-some/msg/fig/diplomat_orig_spring_basic.png")


plt.figure(figsize=(15, 15), dpi=150, facecolor='w', edgecolor='k')
plt.axis("off")
pos = nx.spring_layout(G2, seed=7)
nx.draw_networkx_nodes(G2, pos, node_size = [x*2 for x in node_size], node_color = list(node_color), cmap=plt.get_cmap("tab20"))
nx.draw_networkx_edges(G2, pos, width = [x/100 for x in edge_width], alpha = 0.5)
nx.draw_networkx_labels(G2,pos,labels=list(node_label),font_size=16,font_color='r')
plt.tight_layout()