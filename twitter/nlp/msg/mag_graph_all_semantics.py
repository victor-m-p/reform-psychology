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
G2 = nx.read_gml("/work/cn-some/msg/data/diplomat_wmax.gml", destringizer=int) # takes some time to load

# add interpretation (by hand) 
dimensions = {
    'W_max': [x for x in range(15)],
    'interpretation': ['economy', 'COVID', 'gov', 'Pakistan-Afghanistan', 'gov-proj.', 'new-year', 'embassy', 'Pakistan-peace', 'road(silk)', 'Hong-Kong', 'foreign-affairs', 'life-betterment', 'XiJinping', 'Economy', 'Wang-Yi']
    }

dimension_df = pd.DataFrame(dimensions)
data = data.merge(dimension_df, "inner", "W_max")

# remove self-loops
for edge in G2.edges():
    first, second = edge
    if first == second: 
        G2.remove_edge(*edge)

# get some summary data that we care about
retweets = data.groupby('W_max')['retweet_count'].sum().reset_index()
label = data.groupby('W_max')['interpretation'].apply(pd.Series.mode).reset_index()

# add it to our data 
for i in sorted(G2.nodes()): 
    G2.nodes[retweets.W_max[i]]['retweets'] = retweets.retweet_count[i]
    
# second try for node labels
labeldict = {}
for i in sorted(G2.nodes()): 
    labeldict[i] = label.interpretation[i]

# edge width 
edge_width = nx.get_edge_attributes(G2, 'weight').values() 

# node size & color & label
node_size = nx.get_node_attributes(G2, 'retweets').values()
#node_color = nx.get_node_attributes(G2, 'W_max').values()
node_label = nx.get_node_attributes(G2, 'interpretation').values()

# edge alpha?
width = [x for x in edge_width]
max_width = max(width)

'''
##### with color ######
# spring layout 
plt.figure(figsize=(15, 15), dpi=150, facecolor='w', edgecolor='k')
plt.axis("off")
pos = nx.spring_layout(G2, seed=7)
nx.draw_networkx_nodes(G2, pos, node_size = [x/20 for x in node_size], node_color = [x for x in range(15)], cmap=plt.get_cmap("tab20"))
nx.draw_networkx_edges(G2, pos, width = [x/300 for x in edge_width], alpha = [x/max_width for x in edge_width])
nx.draw_networkx_labels(G2,pos,labels=labeldict,font_size=20,font_color='k')
plt.tight_layout()
plt.show();
plt.savefig("/work/cn-some/msg/fig/diplomat_orig_spring_color.png")

# their layout 
plt.figure(figsize=(15, 15), dpi=150, facecolor='w', edgecolor='k')
plt.axis("off")
pos = graphviz_layout(G2)
nx.draw_networkx_nodes(G2, pos, node_size = [x/20 for x in node_size], node_color = [x for x in range(15)], cmap=plt.get_cmap("tab20"))
nx.draw_networkx_edges(G2, pos, width = [x/300 for x in edge_width], alpha = [x/max_width for x in edge_width])
nx.draw_networkx_labels(G2,pos,labels=labeldict,font_size=20,font_color='r')
plt.tight_layout()
plt.savefig("/work/cn-some/msg/fig/diplomat_orig_graphviz_color.png")
'''

##### without color #######
# inspired by: https://networkx.org/documentation/stable/auto_examples/drawing/plot_chess_masters.html
plt.figure(figsize=(12, 12), facecolor='w', edgecolor='k')
plt.axis("off")
pos = nx.spring_layout(G2, seed=7) # can be tweaked individually. 
nx.draw_networkx_nodes(G2, pos, node_size = [x/500 for x in node_size], node_color = "#210070")
nx.draw_networkx_edges(G2, pos, edge_color = "m", width = [x/6000 for x in edge_width], alpha = [x/max_width for x in edge_width])
label_options = {"ec": "k", "fc": "white", "alpha": 0.7}
nx.draw_networkx_labels(G2,pos,labels=labeldict,font_size=14, bbox=label_options)
plt.tight_layout()
plt.savefig("/work/cn-some/msg/fig/diplomat_all_spring_basic.png")


# moving stuff around 
plt.figure(figsize=(12, 12), facecolor='w', edgecolor='k')
plt.axis("off")
pos = nx.spring_layout(G2, seed=7) # can be tweaked individually. 
pos[4] += (-0.3, -0.3) # gov-proj.
pos[6] += (0.3, 0.5) # embassy 
pos[0] += (-0.2, 0.2) #economy 
pos[13] += (0.3, 0.3) #Economy
#pos[12] += (0, 0.05)
nx.draw_networkx_nodes(G2, pos, node_size = [x/500 for x in node_size], node_color = "#210070")
nx.draw_networkx_edges(G2, pos, edge_color = "m", width = [x/6000 for x in edge_width], alpha = [x/max_width for x in edge_width])
label_options = {"ec": "k", "fc": "white", "alpha": 0.7}
nx.draw_networkx_labels(G2,pos,labels=labeldict,font_size=18, bbox=label_options)
plt.tight_layout()
plt.savefig("/work/cn-some/msg/fig/diplomat_all_spring_tweaked.png")
