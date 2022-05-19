'''
VMP 2022-04-25
visualize topics.
last step in this pipeline.
'''

# imports
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from matplotlib.lines import Line2D
#from community import community_louvain
pd.set_option('display.max_colwidth', None)

# load data
d_backboned = pd.read_csv("/work/50114/twitter/data/nlp/msg/network_tweets/os_rc_5_typeretweet_k100_backbone_df0.8.csv")
d_community = pd.read_csv("/work/50114/twitter/data/nlp/msg/network_tweets/os_rc_5_typeretweet_k100_community_df0.8.csv")
d_topics = pd.read_csv("/work/50114/twitter/data/nlp/msg/network_tweets/os_rc_5_typeretweet_k100_topics.csv")
d_main = pd.read_csv("/work/50114/twitter/data/nlp/msg/network_tweets/os_rc_5_typeretweet_k100_prune2.0.csv")

# check data
d_backboned.head(5) # edge: edgelist, weight
d_community.head(5) # node: community, topic
d_topics.head(5) # node: topic, label, words
d_main.head(5) # edge: original edgelist 

# recode backbone (how about SCORE - do we use this?)
d_backboned = d_backboned.rename(columns = {'nij': 'weight'})

# label communities
## create dictionaries
dct_interpretation = {
    0: "Reproducibility, Replicability & Preregistration",
    1: "Science Training and Communication",
    2: "Publication, Publish/Perish, IF and Badge",
    3: "Publication Process, Peer Review & Preprints",
    4: "Data, Tech, Innovation & Open Access",
    5: "Psychology, RR, Stats, Theory & Preregistration"
}

dct_nodecolor = {
    0: "tab:blue",
    1: "tab:green",
    2: "tab:orange",
    3: "tab:red",
    4: "tab:purple",
    5: "tab:brown"
}

dct_edgecolor = {
    (0, 0): "tab:blue", #1f77b4
    (0, 1): "#268C70", # blue, green
    (0, 2): "#8F7B61", # blue, orange
    (0, 3): "#7B4F6E", # blue, red
    (0, 4): "#5A6FB9", # blue, purple
    (0, 5): "#566780", # blue, brown
    (1, 1): "tab:green", #2ca02c
    (1, 2): "#96901D", # green, orange
    (1, 3): "#81642A", # green, red
    (1, 4): "#608475", # green, purple
    (1, 5): "#5C7B3C", # green, brown
    (2, 2): "tab:orange", #ff7f0e
    (2, 3): "#EB531B", # orange, red
    (2, 4): "#CA7366", # orange, purple
    (2, 5): "#C66B2D", # orange, brown
    (3, 3): "tab:red", #d62728
    (3, 4): "#B54773", # red, purple
    (3, 5): "#B13F3A", # red, brown
    (4, 4): "tab:purple", #9467bd
    (4, 5): "#905F84", # purple, brown
    (5, 5): "tab:brown" #8c564b
}

## create dataframes
d_interpretation = pd.DataFrame(
    dct_interpretation.items(),
    columns = ["community", "interpretation"]
    )

d_nodecolor = pd.DataFrame(
    dct_nodecolor.items(),
    columns = ["community", "color"]
)

## bind with community
d = d_community.merge(d_interpretation, on = "community", how = "inner") # exactly 50
d = d.merge(d_nodecolor, on = "community", how = "inner")

## create network
G = nx.from_pandas_edgelist(
    d_backboned,
    source = "src",
    target = "trg",
    edge_attr = ["weight", "score"]
)

## degree info 
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

## sort dictionary (nodes)
def sort_dictionary(d, sort_val, reverse = True): # here we order it...
    '''
    d: <dict> 
    sort_val: <str>
    '''
    d_sort = dict(sorted(d.items(), key = lambda x: x[1][sort_val], reverse = reverse))
    return d_sort


dct_node = dict(G.nodes(data=True))
dct_weighted = sort_dictionary(dct_node, "weighted_degree", reverse = True)

## add node information
d = d.set_index("topic")
dct_nodeinfo = d.to_dict('index')
nx.set_node_attributes(G, dct_nodeinfo)

## sort dictionary 
def sort_dictionary(d, sort_val, reverse = True): # here we order it...
    '''
    d: <dict> 
    sort_val: <str>
    '''
    d_sort = dict(sorted(d.items(), key = lambda x: x[1][sort_val], reverse = reverse))
    return d_sort


dct_node = dict(G.nodes(data=True))
dct_weighted = sort_dictionary(dct_node, "weighted_degree", reverse = True)

## take out values 
node_list = [key for key, val in dct_weighted.items()]
node_size_list = [val["weighted_degree"] for key, val in dct_weighted.items()]
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

### labels ###
n_labels = 10 # set to 10
dct_labels = defaultdict()
for num, ele in enumerate(node_list): 
    if num < n_labels:
        dct_labels[ele] = ele
    else: 
        dct_labels[ele] = '' 
dct_labels = dict(dct_labels)

## scaling -- not showing all nodes ##
node_divisor = 500
edge_divisor = 10000
node_size = [x/node_divisor for x in node_size_list]
edge_width = [x/edge_divisor if x > 15000 else 0 for x in edge_width_list]

### setup ###
fig, ax = plt.subplots(figsize=(8, 8), dpi=300, facecolor='w', edgecolor='k')
plt.axis("off")

seed = 10 # seed = 10
pos = nx.spring_layout(
    G = G,
    k = 10, # k = 10
    iterations = 2000, 
    seed = seed)

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
    alpha = 1,
    edge_color = edge_color_list) #, 
    #edge_color = edge_color, 
    #arrows=False)

## why no labels now??
nx.draw_networkx_labels(
    G, 
    pos, 
    labels = dct_labels,
    font_size = 10) #, 
    #bbox = label_options,
    #font_weight = 'bold')

## annotate 
ax.annotate("Reproducibility", xy=(.5, .5), xycoords='figure fraction', weight = 'bold', fontsize = 18, color = "tab:blue")
ax.annotate("scicomm/sciedu", xy=(.5, 0.65), xycoords='figure fraction', weight = 'bold', fontsize = 18, color = "tab:green")
ax.annotate("Publish/Perish", xy=(.12, .2), xycoords='figure fraction', weight = 'bold', fontsize = 18, color = "tab:orange")
ax.annotate("Review/Preprints", xy=(.45, .13), xycoords='figure fraction', weight = 'bold', fontsize = 18, color = "tab:red")
ax.annotate("Data", xy=(.12, .52), xycoords='figure fraction', weight = 'bold', fontsize = 18, color = "tab:purple")
ax.annotate("Psychology", xy=(0.23, .67), xycoords='figure fraction', weight = 'bold', fontsize = 18, color = "tab:brown")

## save this plot ## 
outfolder = "/work/50114/twitter/fig/nlp/msg/tweets"
filename = "os_rc_5_typeretweet_k100_prune2.0"
k = 10
nlabels = 10
#plt.tight_layout()
plt.savefig(f"{outfolder}/{filename}_seed{seed}_k{k}_labels{nlabels}_.pdf", bbox_inches='tight')
