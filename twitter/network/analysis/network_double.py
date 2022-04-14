'''
VMP 2022-03-05: 
plotting document.

to-do: 
* pick the right colors 
* (potentially) higher settings for the plot where we do not zoom
* write to pdf instead of png 
* robust in terms of network size (scaling)
* check if they are GCC
* n_labels in main so that it gets saved. 
* set it up to run nicer

time: 
* N = 23719, execution: 4.5 minutes. 
'''

# packages
import pandas as pd 
import numpy as np
import re
import networkx as nx 
import matplotlib.pyplot as plt 
import timeit
from pathlib import Path
import argparse 

# gather queries
def gather_queries(dfs, labels): 
    ''' 
    dfs: <list> list of two <pd.dataframe>
    labels: <list> list of two <str> 

    '''
    
    # unpack 
    d1, d2 = dfs 
    label1, label2 = labels

    # bind two frames
    df = pd.concat([d1, d2])
    df.groupby(['username_from', 'username_to'])['weight'].sum().reset_index(name = 'weight')

    # add identifier
    d1["query_x"] = label1
    d1["query_y"] = label2

    # delete weight in indicator dataframes
    d1 = d1.drop(columns = {'weight'})
    d2 = d2.drop(columns = {'weight'})

    ## merge stuff
    d1_merged = df.merge(d1, on = ['username_from', 'username_to'], how = 'outer')
    d2_merged = d1_merged.merge(d2, on = ['username_from', 'username_to'], how = 'outer')

    ## bring it together
    conditions = [
        (d2_merged['query_x'] == f'{label1}') & (d2_merged['query_y'].isnull()),
        (d2_merged['query_x'].isnull()) & (d2_merged['query_y'] == f'{label2}')]
    choices = [f'{label1}', f'{label2}']

    d2_merged['query'] = np.select(conditions, choices, default = 'both')
    d_clean = d2_merged.drop(columns = {'query_x', 'query_y'})

    return d_clean

# get maximum, important for dividing. 
def get_maximum(df): 
    '''
    df: <pd.dataframe> 
    '''
    max_edge = df["weight"].max() 
    df_from = df.groupby('username_from')['weight'].sum().reset_index().rename(columns = {
        'username_from': 'username',
        'weight': 'weight_from'}).fillna(0)
    df_to = df.groupby('username_to')['weight'].sum().reset_index().rename(columns = {
        'username_to': 'username',
        'weight': 'weight_to'}).fillna(0)
    df_gathered = df_from.merge(df_to, on = 'username', how = 'outer').fillna(0)
    df_gathered = df_gathered.assign(total_weight = lambda x: x["weight_from"] + x["weight_to"])
    max_node = df_gathered["total_weight"].max()
    return max_edge, max_node

def subset_cutoff(df, n):
    '''
    df: <pd.dataframe> 
    n: <int> 
    '''
    print(f"before cut-off: {len(df)}")
    df = df[df["weight"] > n]
    print(f"after cut-off: {len(df)}")
    return df

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

#### plot ####
def plot_network(G, node_size_lst, edge_width_lst, node_divisor, edge_divisor, title, filename, outfolder, seed, k, labeldict = None):
    '''
    G: <networkx.classes.digraph.DiGraph> 
    node_size_lst: <list> node sizes 
    edge_width_lst: <list> edge width
    node_divisor: <int/float> scaling for all node sizes 
    edge_divisor: <int/float> scaling for all edges 
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
    nx.draw_networkx_nodes(G, pos, node_size=node_size, node_color = "#ffbb00") #, node_size = node_size, node_color = node_color)
    nx.draw_networkx_edges(G, pos, width = edge_width, alpha = 0.5, arrows=False, edge_color = "#ffcf4d") #, edge_color = edge_col)

    # labels 
    labels = 'False'
    if labeldict: 
        label_options = {"edgecolor": "none", "facecolor": "white", "alpha": 0}
        nx.draw_networkx_labels(G,pos,labels=labeldict,font_size=6, bbox=label_options)
        labels = 'True'

    plt.suptitle(f'{title}', size=50)
    plt.tight_layout()
    plt.savefig(f"{outfolder}/{filename}_seed{seed}_k{k}_labels{labels}.png", bbox_inches='tight')

def main(inpath, outpath, query1, query2, cutoff, nlabels): 

    # set vars 
    k = None 
    seed = 8

    # timeit
    starttime = timeit.default_timer()

    # read data
    df1 = pd.read_csv(f"{inpath}/{query1}_edgelist_simple.csv")
    df2 = pd.read_csv(f"{inpath}/{query2}_edgelist_simple.csv")

    # prepare lists 
    df_list = [df1, df2]
    query_list = [query1, query2]

    # merge the two 
    d_clean = gather_queries(df_list, query_list)

    # subset data (cutoff = 0 if to avoid)
    df = subset_cutoff(d_clean, cutoff) 

    # networkx 
    G = nx.from_pandas_edgelist(df, source='username_from', target='username_to', edge_attr='weight', create_using=nx.DiGraph())

    # get maximum edge and node (for division)
    max_edge, max_node = get_maximum(df)

    # width by weight
    edge_weights = nx.get_edge_attributes(G, 'weight').values() 

    # size by degree
    weighted_degree = degree_information(G, G.degree(weight='weight'), "weighted_degree")

    # labels
    labeldict_degreew = get_labels(G, 'weighted_degree', weighted_degree, nlabels)

    #### author information #### 
    # create the plot where we zoom
    node_divisor = max_node / 1800 # (2) max_node / (max_node/2)
    edge_divisor = max_edge / 3 # (10) max_edge / (max_edge/10)

    # plot set-up
    filename = f'{query1}_{query2}_ZOOM'
    title = "" # no title for now 

    print("--- starting first plot ---")
    # plot it 
    plot_network(
        G = G, 
        node_size_lst = weighted_degree, 
        edge_width_lst = edge_weights, 
        node_divisor = node_divisor,
        edge_divisor = edge_divisor,
        title = title,
        filename = filename,
        outfolder = outpath,
        seed = seed,
        k = k,
        labeldict = labeldict_degreew
    )

    #### create the plot where we do not zoom ####
    node_divisor = max_node / 900 # (1)
    edge_divisor = max_edge / 8 # (2)

    filename = f'{query1}_{query2}_NOZOOM'
    
    print("--- starting second plot ---")
    plot_network(
        G = G, 
        node_size_lst = weighted_degree, 
        edge_width_lst = edge_weights, 
        node_divisor = node_divisor, 
        edge_divisor = edge_divisor, 
        title = title, 
        filename = filename, 
        outfolder = outpath,
        seed = seed,
        k = k
    )
    
    endtime = timeit.default_timer()
    totaltime = endtime - starttime 
    print(f"execution time: {round(totaltime/60, 2)} minutes")

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--inpath", required = True, type = str, help = "path to input folder (edgelist_simple)")
    ap.add_argument("-o", "--outpath", required = True, type = str, help = "path to output folder (for pdfs)")
    ap.add_argument("-q1", "--query1", required = True, type = str, help = "query, e.g. openscience")
    ap.add_argument("-q2", "--query2", required = True, type = str, help = "query, e.g. openscience")
    ap.add_argument("-c", "--cutoff", required = True, type = int, help =  "edges with weight below cutoff excluded")
    ap.add_argument("-n", "--nlabels", required = True, type = int, help = "how many labels to display")  
    args = vars(ap.parse_args())

    main(
        inpath = args["inpath"],
        outpath = args["outpath"],
        query1 = args["query1"],
        query2 = args["query2"],
        cutoff = args["cutoff"],
        nlabels = args["nlabels"]
    )