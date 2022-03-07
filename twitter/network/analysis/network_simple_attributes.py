'''
VMP 2022-03-05: 
plotting document.

to-do: 
* find good colors
* good edge-color (or attribute)
* why do we have na (i.e. authors in network but not in meta-data?)
* add legend explaining colors 
'''

# packages 
import pandas as pd 
import numpy as np
import re
import networkx as nx 
import matplotlib.pyplot as plt 

# visual setup 

# load file
df = pd.read_csv("/work/50114/twitter/data/network/preprocessed/bropenscience_edgelist_simple.csv")

# networkx 
G = nx.from_pandas_edgelist(df,source='username_from',target='username_to', edge_attr='weight', create_using=nx.DiGraph())

#### edge attributes ####

# width by weight
edge_weights = nx.get_edge_attributes(G, 'weight').values() 


#### node size ####
def degree_information(G, method, metric):
    '''
    G: <networkx.classes.digraph.DiGraph
    method: G.degree() or variants 
    metric: <str> e.g. "weighted_degree" 
    '''

    degree = {node:val for (node, val) in method}
    nx.set_node_attributes(G, degree, metric)
    degree = nx.get_node_attributes(G, metric).values()
    return degree

# size by degree
weighted_degree = degree_information(G, G.degree(weight='weight'), "weighted_degree")

#### add labels for central actors ####
def get_labels(G, type_str, type_lst, n_labels):
    '''
    type_str: <str> e.g. "mentions" 
    type_lst: <list> corresponding.
    n_labels: <int> number of labels
    '''

    # sort list and take top 
    lst_sorted = sorted(type_lst, reverse=True)
    cutoff = lst_sorted[n_labels]
    
    # loop over them and assign labels to greater than cutoff 
    labels = nx.get_node_attributes(G, type_str)
    labeldict = {}
    for key, val in labels.items(): 

        if val > cutoff: 
            labeldict[key] = key
        else: 
            labeldict[key] = ''
    
    return labeldict 

n_labels = 10
labeldict_degreew = get_labels(G, 'weighted_degree', weighted_degree, n_labels)

#### author information ###
df_author = pd.read_csv("/work/50114/twitter/data/network/preprocessed/bropenscience_authors.csv")

# gender
def get_attribute(G, df, id_column, attr_column, color_dct): 

    '''
    G: <networkx.classes.digraph.DiGraph>
    df: <pd.dataframe>
    id_column: <str> id column to match nodes
    attr_column: <str> attribute column 
    color_dct: <dict> dictionary with color codes
    '''

    # get nodes in G
    df_nodes = pd.DataFrame(G.nodes(), columns = ['username'])
    # merge left with our attribute df
    df_clean = df_nodes.merge(df_author, on = "username", how = "left")
    # fill na to "unknown" (actually, why do we have na?)
    df_clean['gender'] = df_clean['gender'].fillna('unknown')
    # zip it 
    attr_dct = dict(zip(df_clean[id_column], df_clean[attr_column]))
    nx.set_node_attributes(G, attr_dct, attr_column)
    attr_lst = nx.get_node_attributes(G, attr_column).values()
    attr_color = [color_dct.get(x) for x in attr_lst]
    return attr_color

color_dct = {'male': 'tab:blue', 'female': 'tab:orange', 'unknown': 'tab:gray'}
gender_color = get_attribute(
    G = G, 
    df = df_author, 
    id_column = "username",
    attr_column = "gender",
    color_dct = color_dct
)

#### plot ####
def plot_network(G, node_size_lst, edge_width_lst, node_divisor, edge_divisor, node_color, edge_color, title, filename, outfolder, seed = 8, k = None, labeldict = None):
    '''
    G: <networkx.classes.digraph.DiGraph> 
    node_size_lst: <list> node sizes 
    edge_width_lst: <list> edge width
    node_divisor: <int/float> scaling for all node sizes 
    edge_divisor: <int/float> scaling for all edges 
    node_color: <list> or <str>
    edge_color: <list> or <str>
    title: <str> plot title 
    filename: <str> filename 
    seed: <int> optional seed for pos (default: 8)
    k: <float> optional configuration of spacing for pos (default: None)
    labeldict: <dict> optional labels (defalt: None)
    ''' 

    # setup 
    fig, ax = plt.subplots(figsize=(24, 24), dpi=200, facecolor='w', edgecolor='k')
    plt.axis("off")
    
    # pos 
    pos = nx.spring_layout(G, k = k, seed = seed)

    # set up 
    node_size = [node_degree/node_divisor for node_degree in node_size_lst]
    edge_width =  [edge_weight/edge_divisor for edge_weight in edge_width_lst]

    # draw it 
    nx.draw_networkx_nodes(G, pos, node_size=node_size, node_color = node_color) #, node_size = node_size, node_color = node_color)
    nx.draw_networkx_edges(G, pos, width = edge_width, alpha = 0.5, arrows=False, edge_color = edge_color) #, edge_color = edge_col)

    # labels 
    labels = 'False'
    if labeldict: 
        label_options = {"edgecolor": "none", "facecolor": "white", "alpha": 0}
        nx.draw_networkx_labels(G,pos,labels=labeldict,font_size=6, bbox=label_options)
        labels = 'True'

    plt.suptitle(f'{title}', size=50)
    plt.tight_layout()
    plt.savefig(f"{outfolder}/{filename}_attr_seed{seed}_k{k}_labels{labels}.png", bbox_inches='tight')

# create the plot where we zoom
node_divisor = 2
edge_divisor = 10
title = 'bropenscience network'
outfolder = '/work/50114/twitter/fig/network/simple'
filename = 'bropenscience'

plot_network(
    G = G, 
    node_size_lst = weighted_degree, 
    edge_width_lst = edge_weights, 
    node_divisor = node_divisor,
    edge_divisor = edge_divisor,
    node_color = gender_color,
    edge_color = 'tab:grey', # not sure what this should ee
    title = title,
    filename = filename,
    outfolder = outfolder,
    labeldict = labeldict_degreew
)

# create the plot where we do not zoom
node_divisor = 1
edge_divisor = 2
title = 'bropenscience network'
outfolder = '/work/50114/twitter/fig/network/simple'
filename = 'bropenscience'

plot_network(
    G = G, 
    node_size_lst = weighted_degree, 
    edge_width_lst = edge_weights, 
    node_divisor = node_divisor, 
    edge_divisor = edge_divisor, 
    node_color = gender_color, 
    edge_color = 'tab:grey',
    title = title, 
    filename = filename, 
    outfolder = outfolder
)
