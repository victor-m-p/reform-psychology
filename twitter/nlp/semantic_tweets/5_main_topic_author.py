'''
VMP 2022-04-22: 
topics over time 
'''

# read stuff (test on bropenscience)
# imports
import numpy as np 
import matplotlib.pyplot as plt 
import networkx as nx 
import pandas as pd 
import pickle
import seaborn as sns
from matplotlib.lines import Line2D
from collections import defaultdict
pd.set_option('display.max_colwidth', None)

def read_pickle(inpath): 
    with open(f"{inpath}", "rb") as f: 
        d = pickle.load(f)
    return d 

# what do we need # (could backbone this) 
d_edgelist = read_pickle("/work/50114/twitter/data/nlp/semantic_info/semantic_edgelist.pickle")
d_backboned = read_pickle("/work/50114/twitter/data/nlp/backboning/os_rc_5_intersection_bb_df_threshold0.9.pickle")
d_authorattr = read_pickle("/work/50114/twitter/data/nlp/semantic_info/author_attributes.pickle")

# setup
dct_interpretation = { # do we actually use this?
    0: "Publication", # 183
    1: "Culture & Training", # 154
    2: "Data & Policy", # 53
    3: "Reform Psychology", # 315
    4: "OSF", # 26
    1000: "None" # 7
}

dct_nodecolor = {
    0: "tab:blue",
    1: "tab:green",
    2: "tab:orange",
    3: "tab:red",
    4: "tab:purple",
    1000: "tab:brown"
}

dct_edgecolor = {
    (0, 0): "tab:blue", #1f77b4
    (0, 1): "#268C70", # blue, green
    (0, 2): "#8F7B61", # blue, orange
    (0, 3): "#7B4F6E", # blue, red
    (0, 4): "#5A6FB9", # blue, purple
    (0, 1000): "#566780", # blue, brown
    (1, 1): "tab:green", #2ca02c
    (1, 2): "#96901D", # green, orange
    (1, 3): "#81642A", # green, red
    (1, 4): "#608475", # green, purple
    (1, 1000): "#5C7B3C", # green, brown
    (2, 2): "tab:orange", #ff7f0e
    (2, 3): "#EB531B", # orange, red
    (2, 4): "#CA7366", # orange, purple
    (2, 1000): "#C66B2D", # orange, brown
    (3, 3): "tab:red", #d62728
    (3, 4): "#B54773", # red, purple
    (3, 1000): "#B13F3A", # red, brown
    (4, 4): "tab:purple", #9467bd
    (4, 1000): "#905F84", # purple, brown
    (1000, 1000): "tab:brown" #8c564b
}

## create network
d_backboned = d_backboned.rename(columns = {'nij': 'weight'})
G = nx.from_pandas_edgelist(
    d_backboned,
    source = "src",
    target = "trg",
    edge_attr = ["weight", "score"]
)

## GCC
largest_cc = max(nx.connected_components(G), key=len)
G = G.subgraph(largest_cc)

## by degree in the network
def degree_information(G, method, metric):
    '''
    G: <networkx.classes.digraph.DiGraph
    method: G.degree() or variants 
    metric: <str> e.g. "weighted_degree" 
    '''

    degree = {node:val for (node, val) in method}
    nx.set_node_attributes(G, degree, metric)
    return G

degree_information(G, G.degree(weight = "weight"), "weighted_degree")

## eigenvector centrality
centrality = nx.eigenvector_centrality(G)
nx.set_node_attributes(G, centrality, "eigenvector")

## add node information
d_interpretation = pd.DataFrame(
    dct_interpretation.items(),
    columns = ["community", "interpretation"]
    )

d_nodecolor = pd.DataFrame(
    dct_nodecolor.items(),
    columns = ["community", "color"]
)

## bind with community
d = d_authorattr.merge(d_interpretation, on = "community", how = "inner") # exactly 50
d = d.merge(d_nodecolor, on = "community", how = "inner")
d_index = d.set_index('username')
dct_nodeinfo = d_index.to_dict('index')
nx.set_node_attributes(G, dct_nodeinfo)

## sort dictionary (nodes)
def sort_dictionary(d, sort_val, reverse = True): # here we order it...
    '''
    d: <dict> 
    sort_val: <str>
    '''
    d_sort = dict(sorted(d.items(), key = lambda x: x[1][sort_val], reverse = reverse))
    return d_sort

sort_val = "weighted_degree" # weighted_degree, retweet_sum, followers
dct_node = dict(G.nodes(data=True))
dct_weighted = sort_dictionary(dct_node, sort_val, reverse = True)

## take out values 
node_list = [key for key, val in dct_weighted.items()]
node_size_list = [val[sort_val] for key, val in dct_weighted.items()] # depends on sort_val (fine)
node_eigenvector_list = [val["eigenvector"] for key, val in dct_weighted.items()]
node_color_list = [val["color"] for key, val in dct_weighted.items()] 
node_label_list = [val["interpretation"] for key, val in dct_weighted.items()] 
node_community_list = [val["community"] for key, val in dct_weighted.items()] 

## extract edge weight
edgeattr_weight = nx.get_edge_attributes(G, "weight") ## need to sort here as well
edge_width_list = list(edgeattr_weight.values())

## extract edge color (should be whether edge crosses community I think)
for i, j in G.edges():
    # find the communities
    comm_i = dct_weighted.get(i)["community"]
    comm_j = dct_weighted.get(j)["community"]

    # sort the values
    comm_low, comm_high = sorted([comm_i, comm_j])

    # find the color 
    comm_col = dct_edgecolor.get((comm_low, comm_high))

    # assign color
    G[i][j]['color'] = comm_col

## extract it 
edgeattr_color = nx.get_edge_attributes(G, "color")
edge_color_list = list(edgeattr_color.values())

###### intermezzo ###### 

## by eigenvector centrality 
# 1. BrianNosek: nosek (OSF, open science, psychology) 
# 2. chrisdc77: Chris chambers (registered reports, replications, psychology)
# 3. lakens: Daniel Lakens (psychology, statistics)
# 4. OSFramework: ...
# 5. nicebread303: Felix Schönbrodt (psychology, open science, statistics)
# 6. hardsci: Sanjay Srivastava: methods + openscience
# 7. siminevazire: Simine Vazire: psychology, collabraOA, science credibility
# 8. giladfeldman: Gilad Feldman: open/meta-science, psychology, prereg, mass replication
# 9. aeryn_thrace: M. González-Márquez: science comm, theory-building
# 10. hansijzerman: Hans Rocha: psysciacc, meta-science
# 14: o_guest: bropenscience, theory 
# ...: zerdeve, IrisVanRooij 

## by weighted degree 
# 1. BrianNosek
# 2. chrisdc77
# 3. OSFramework
# 4. nicebread303 
# 5. giladfeldman
# 6. o_guest 
# 7. lakens 
# 8. hardsci 
# 9. Leibniz Research -- institute 
# 10. RickyPo -- journalist 
# ...: IrisVanRooij (much higher), zerdeve (higher). 

## NB: kind of interesting that some of the accounts rank much higher
## on weighted degree (just the number of interactions-activity) 
## specifically, the fact that o_gust, IrisVanRooij and zerdeve 
## are higher on weighted degree than on eigenvector centrality 
## suggests that they are less well connected to other central nodes
## i.e., this is sort of the mechanism of eigenvector centrality. 
## I think that we should just make the network plots for weighted degree
## and then have it as a perspective (i.e. that although the network seems
## pretty even, there is something where important/central accounts cluster
## together -- and it makes sense that this does not include the sceptics). 

## by retweet_sum
# 1. BrianNosek 
# 2. figshare 
# 3. OpenSci_News 
# 4. OSFramework 
# 5. fosterscience 
# 6. chrisdc77
# 7. PLOS
# 8. Science_Open
# 9. brembs 
# 10. lfvopenscience

#### plot of top people on both eigenvector centrality and on weighted degree ####

## (1) eigenvector centrality ## 
outfolder = "/work/50114/twitter/fig/network/semantic"
dct_eigen = sort_dictionary(dct_node, "eigenvector", reverse = True)
lst_eigen = [(key, val["eigenvector"]) for key, val in dct_eigen.items()]
df_eigen = pd.DataFrame(lst_eigen, columns = ["username", "eigenvector"])
df_eigen["rank"] = df_eigen.index + 1
df_eigen = df_eigen.merge(d, on = "username", how = "inner")
df_eigen.to_csv("/work/50114/twitter/data/nlp/centrality_report/eigenvector.csv", index = False)
df_eigen_top = df_eigen.head(10)

## plot (matplotlib)
fig, ax = plt.subplots(figsize=(3.5,4), dpi = 100)
x_val = df_eigen_top["username"]
y_val = df_eigen_top["eigenvector"]
c_val = df_eigen_top["color"]
plt.barh(x_val, y_val, color = c_val)
ax.invert_yaxis()
plt.xlabel('Eigenvector centrality')
plt.savefig(f"{outfolder}/top10_eigenvector_centrality_new.pdf", bbox_inches='tight')


## (2) weighted degree ## 
#d_weighted = 
#dct_weighted = sort_dictionary(dct_node, sort_val, reverse = True)
dct_weight = sort_dictionary(dct_node, "weighted_degree", reverse = True)
lst_weight = [(key, val["weighted_degree"]) for key, val in dct_weight.items()]
df_weight = pd.DataFrame(lst_weight, columns = ["username", "weighted_degree"])
df_weight["rank"] = df_weight.index + 1
df_weight = df_weight.merge(d, on = "username", how = "inner")
df_weight.to_csv("/work/50114/twitter/data/nlp/centrality_report/weighted_degree.csv", index = False)
df_weight_top = df_weight.head(10)

## plot (matplotlib)
fig, ax = plt.subplots(figsize=(3.5,4), dpi = 100)
x_val = df_weight_top["username"]
y_val = df_weight_top["weighted_degree"]
c_val = df_weight_top["color"]
plt.barh(x_val, y_val, color = c_val)
ax.invert_yaxis()
plt.xlabel('Weighted degree')
plt.savefig(f"{outfolder}/top10_weighted_degree_new.pdf", bbox_inches='tight')

###### back to network #######

## labels
n_labels = 10 # set to 10
dct_labels = defaultdict()
for num, ele in enumerate(node_list): 
    if num < n_labels:
        dct_labels[ele] = ele
    else: 
        dct_labels[ele] = '' 
dct_labels = dict(dct_labels)

## scaling ##
node_divisor = 10 # 10 for weighted_degree
edge_divisor = 10
node_size = [x/node_divisor for x in node_size_list]
edge_width = [x/edge_divisor if x > 5 else 0 for x in edge_width_list]

### setup ###
fig, ax = plt.subplots(figsize=(7, 5), dpi=300, facecolor='w', edgecolor='k')
plt.axis("off")

seed = 20 # good: 13
k = None
pos = nx.spring_layout(
    G = G,
    k = k,
    iterations = 100,
    seed = seed)

## nudge stuff
#pos[71] += (0, -0.05) # (x, y)

nx.draw_networkx_nodes(
        G, 
        pos, 
        nodelist = node_list, 
        node_size = node_size, 
        node_color = node_color_list,
        edgecolors = "black",
        linewidths = 0.5)

nx.draw_networkx_edges(
    G, 
    pos, 
    #edgelist = edgelst, 
    width = edge_width, 
    alpha = 0.5,
    edge_color = edge_color_list) 

plt.tight_layout()
filename = "openscience_replicationcrisis"
outfolder = "/work/50114/twitter/fig/network/semantic"
plt.savefig(f"{outfolder}/{filename}_seed{seed}_k{k}_labelsFALSE_new.pdf", bbox_inches='tight')

### plot with crazy good resolution & labels ###
node_divisor = 7 # 10 for weighted_degree (a bit larger)
edge_divisor = 10
node_size = [x/node_divisor for x in node_size_list]
edge_width = [x/edge_divisor if x > 25 else 0 for x in edge_width_list]

### setup ###
fig, ax = plt.subplots(figsize=(14, 10), dpi=300, facecolor='w', edgecolor='k')
plt.axis("off")

seed = 20 # good: 13, 15 
pos = nx.spring_layout(
    G = G,
    k = None,
    iterations = 100,
    seed = seed)

## nudge stuff
pos["nicebread303"] += (0, -0.05) # (x, y)

nx.draw_networkx_nodes(
        G, 
        pos, 
        nodelist = node_list, 
        node_size = node_size, 
        node_color = node_color_list, 
        edgecolors = "black",
        linewidths = 0.5)

nx.draw_networkx_edges(
    G, 
    pos, 
    #edgelist = edgelst, 
    width = edge_width, 
    alpha = 0.5,
    edge_color = edge_color_list) 

# draw labels 
nx.draw_networkx_labels(
    G, 
    pos, 
    labels = dct_labels,
    bbox = {"ec": "black", "fc": "white", "alpha": 0.6, 'pad': 0.5},
    font_size = 5,
    font_weight = 'bold');

plt.tight_layout()
outfolder = "/work/50114/twitter/fig/network/semantic"
plt.savefig(f"{outfolder}/{filename}_seed{seed}_k{k}_labelsTRUE_new.pdf", bbox_inches='tight')
