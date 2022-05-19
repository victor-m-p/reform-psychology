'''
VMP 2022-04-19:
TODO: 
* break ties randomly
* weighting by e.g. retweets
'''

import argparse
import os
import numpy as np
from sklearn.metrics import pairwise_distances
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt
import pandas as pd
import itertools 
import time 


A = np.eye(5)
A[1, 2] = 2
A

# test something 
print(A.shape)

# could be A > anything... (also our cutoff)
B = (A > 0).tolist()
B
A[A.nonzero()]

## another solution
# just actually sets all of the shit to zero
# should be faster?
a[a > 10] = 0 



## NB: many communities -- does not seem useful 
## NB: graph-id -- also not sure what to use it for. 
## TWO-THINGS: 
# (1) color users by their maximum W 
# (2) network only based on relations within semantic space
# (3) probably want more W_max categories so that communities make more sense --- 
#### or to run community detection on the small thing ####

# Assumption: every row in data corresponds to row/col in data W/nmf 
# We can assign maximum W by using index 

# load stuff
data = pd.read_csv("/work/50114/twitter/data/nlp/msg/bropenscience_tweet_text_stopwords_k15_nmf.csv")
G = nx.read_gml("/work/50114/twitter/data/nlp/msg/bropenscience_tweet_text_stopwords_k15_G.gml", destringizer=int) # takes some time to load
W = np.loadtxt("/work/50114/twitter/data/nlp/msg/bropenscience_tweet_text_stopwords_k15_W.txt")

### test D ###
print(W.shape) # how much each tweet is in each category - could cap here instead of max


D = pairwise_distances(W, metric = "cosine", njobs = -1)
print(D.shape)

# add interpretation (by hand) 
dimensions = {
    'W_max': [x for x in range(15)],
    'interpretation': ['economy', 'COVID', 'gov', 'Pakistan-Afghanistan', 'gov-proj.', 'new-year', 'embassy', 'Pakistan-peace', 'road(silk)', 'Hong-Kong', 'foreign-affairs', 'life-betterment', 'XiJinping', 'Economy', 'Wang-Yi']
    }

dimension_df = pd.DataFrame(dimensions)
data = data.merge(dimension_df, how = "inner", on = "W_max")

# get edgelist 
edgelist = nx.to_pandas_edgelist(G)

# add index
data['index'] = data.index

# label by author 
label = data.groupby('username')['interpretation'].apply(pd.Series.mode).reset_index() ## assigning MAX to node
label.groupby('level_1').size() # need to break ties randomly actually
label = label[label["level_1"] == 0]
label = label[["username", "interpretation"]]
label = label.rename(columns = {'interpretation': 'category'})
label_data = data.merge(label, on = "username", how = 'inner')

# add 
d_labels = label_data[['index', 'category']]

d_labels = d_labels.rename(columns = {
    'index': 'source',
    'category': 'src_category'})

edgelist = edgelist.merge(d_labels, on = "source", how = "inner")

d_labels = d_labels.rename(columns = {
    'source': 'target',
    'src_category': 'trg_category'
})

edgelist = edgelist.merge(d_labels, on = "target", how = "inner")

# remove self-loops 
edgelist_clean = edgelist[edgelist["src_category"] != edgelist["trg_category"]]
edgelist_weight = edgelist_clean.groupby(['src_category', 'trg_category'])['weight'].sum().reset_index(name = 'weight')

# re-order to undirected 
def directed_to_undirected(d, c_weight, c_src, c_trg): 
    '''
    d: <pd.dataframe> directed dataframe
    c_weight: <str> weight column name
    c_src: <str> src column name
    c_trg: <str> trg column name 
    '''
    dct = {}
    for index, row in d.iterrows(): 

        # take data out 
        weight = row[c_weight]
        src = row[c_src]
        trg = row[c_trg]

        # sort values
        src, trg = sorted([src, trg])

        # put into dict 
        dct[index] = {
            'src': src,
            'trg': trg, 
            'weight': weight
        }

    # put into frame 
    d = pd.DataFrame.from_dict(dct, "index")
    d = d.groupby(['src', 'trg'])['weight'].sum().reset_index(name = 'weight')
    return d

# run function
d_weighted = directed_to_undirected(
    edgelist_weight,
    "weight",
    "src_category",
    "trg_category"
)
    
# create network
G = nx.from_pandas_edgelist(
    d_weighted, 
    source = 'src',
    target = 'trg',
    edge_attr = 'weight',
    create_using = nx.Graph()
)

## attributes
# largest by most number 1 (could be better I guess)
size_categories = data.groupby('interpretation').size().reset_index(name = 'size')
dct_categories = dict(zip(size_categories["interpretation"], size_categories["size"]))
nx.set_node_attributes(G, dct_categories, "size")

# labels (for largest) 
node_label_size = nx.get_node_attributes(G, "size")
node_size = sorted(list(node_label_size.values()), reverse = True)
cutoff = node_size[5] # display five largest
labeldict = {}

for key, val in node_label_size.items(): 
    if val > cutoff: 
        labeldict[key] = key
    else: 
        labeldict[key] = ''

# visualize (NB: perhaps prune this) 
## setup
seed = 123
fig, ax = plt.subplots(figsize=(8, 8), dpi=300, facecolor='w', edgecolor='k')
plt.axis("off")
pos = nx.spring_layout(
            G = G,
            seed = seed
        )

## node and edge size 
node_divisor = 2
edge_divisor = 2

node_size_lst = sorted(list(nx.get_node_attributes(G, "size").values()))
node_size = [x/node_divisor for x in node_size_lst]

edge_width_lst = sorted(list(nx.get_edge_attributes(G, "weight").values()))
edge_width = [x/edge_divisor for x in edge_width_lst]

nx.draw_networkx_nodes(
        G, 
        pos, 
        node_size = node_size)

nx.draw_networkx_edges(
    G, 
    pos, 
    width = edge_width, 
    alpha = 0.5, 
    arrows=False)

## community detection
from community import community_louvain
parts = community_louvain.best_partition(G)







##### OLD WAY #####
# remove self-loops
for edge in G.edges():
    first, second = edge
    if first == second: 
        G.remove_edge(*edge)

# give names to nodes: NB: nodes are tweets here!!!
data['index'] = data.index
d_handle = dict(zip(data["index"], data["username"]))
nx.set_node_attributes(G, d_handle, "username")

# get some summary (node) data that we care about
# retweets = data.groupby('W_max')['retweet_count'].sum().reset_index() ## could make sense in terms of popularity
label = data.groupby('username')['interpretation'].apply(pd.Series.mode).reset_index() ## assigning MAX to node
label.groupby('level_1').size() # need to break ties randomly actually
label = label[label["level_1"] == 0]
label = label[["username", "interpretation"]]
label = label.rename(columns = {'interpretation': 'category'})
label_data = data.merge(label, on = "username", how = 'inner')

# second try for node labels
d_category = dict(zip(label_data["index"], label_data["category"]))
nx.set_node_attributes(G, d_category, "category")

#labeldict = {}
#for node, data in G.nodes(data=True):
#    username = data['username']
#    category = label[label['username'] == username].category[0]
#    labeldict[username] = category
#    node["category"] = category


#labeldict = {}
#for i in sorted(G.nodes()): 
#    labeldict[i] = label.interpretation[i]

## do it with edgelist: 
# NB: in this case we do not care about nodes, only about W 
# need to collapse this to (e.g. W1 --> W3)


## make it undirected (function from earlier) 
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



# create network 
edgelist_weight.groupby('src_category').size()



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
