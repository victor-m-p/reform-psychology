'''
NB: becomes main file (2022-04-09)

to-do: 
* add proper args to get_legend
'''

# imports 
import pandas as pd 
import numpy as np
import networkx as nx 
import matplotlib.pyplot as plt
from statistics import median
import math
from matplotlib.lines import Line2D
import argparse 
from pathlib import Path
from collections import defaultdict

## functions ## 

# maximum node and edge (for scaling) 
def get_maximum(df, src, trg, nij): 
    '''
    df: <pd.dataframe> 
    src: <str> source column name 
    trg: <str> target column name 
    nij: <str> weight column name 
    score: <str> score column name 
    '''

    max_edge = df[nij].max() 
    df_from = df.groupby(src)[nij].sum().reset_index().rename(columns = {
        src: 'username',
        nij: 'weight_from'}).fillna(0)
    df_to = df.groupby(trg)[nij].sum().reset_index().rename(columns = {
        trg: 'username',
        nij: 'weight_to'}).fillna(0)
    df_gathered = df_from.merge(df_to, on = 'username', how = 'outer').fillna(0)
    df_gathered = df_gathered.assign(total_weight = lambda x: x["weight_from"] + x["weight_to"])
    max_node = df_gathered["total_weight"].max()
    return max_edge, max_node

# degree information
def degree_information(G, method, metric):
    '''
    G: <networkx.classes.digraph.DiGraph
    method: G.degree() or variants 
    metric: <str> e.g. "weighted_degree" 
    '''

    degree = {node:val for (node, val) in method}
    nx.set_node_attributes(G, degree, metric)

''' sort values '''

#### labels ####
# labels mentions 
def get_labels(G, type_str, type_lst, n_labels, focus_handles = False):
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

        if focus_handles and key in focus_handles: 
            labeldict[key] = key

        elif val > cutoff: 
            labeldict[key] = key
        
        else: 
            labeldict[key] = ''
        
    return labeldict 

#### general plot setup #### 
def get_legend(node_size_list, colors_dct, labels_dct, query1, query2): # add proper args
    
    #node_median = np.mean(node_size_list) #median(node_size_list) 
    #right now we do not use node_size_list for scaling. 
    
    lines = [
        Line2D([0], [0], linewidth=0, markersize = 10, color = colors_dct.get(f'{query1}'), marker='o'), #math.sqrt(node_median)
        Line2D([0], [0], linewidth=0, markersize = 10, color = colors_dct.get(f'{query2}'), marker='o'),
        Line2D([0], [0], linewidth=0, markersize = 10, color = colors_dct.get('Overlap'), marker = 'o')
            ] 

    label1 = labels_dct.get(f"{query1}")
    label2 = labels_dct.get(f"{query2}")
    labels = [f'{label1}', f'{label2}', 'Overlap']
    
    return lines, labels

def nudge_position(pos, nudge_triple):
    '''
    pos: nx.spring_layout
    nudge_triple: <list> list of triples with name, x, y. 
    '''
    for name, x, y in nudge_triple:
        pos[name] += (x, y) 
    return pos

def sort_dictionary(d, sort_val, reverse = True): 
    '''
    d: <dict> 
    sort_val: <str>
    '''
    d_sort = dict(sorted(d.items(), key = lambda x: x[1][sort_val], reverse = reverse))
    return d_sort

def add_color(dct_nodecolor, dct_nodeedgecolor, category_lst): 
    '''
    dct_nodecolor: <dict>
    dct_nodeedgecolor: <dict>
    category_list: <list>
    '''
    node_color = [dct_nodecolor.get(x) for x in category_lst] 
    node_edgecolor = [dct_nodeedgecolor.get(x) for x in category_lst]
    return node_color, node_edgecolor 

# extract values for each network
def extract_values(dct, color_var, size_var): 
    '''
    dct: <dict> (sorted)
    color_var: <str> color variable (e.g. "color" or "category")
    size_var: <str> size variable (e.g. "degree" or "weight")
    '''
    lst = []
    lst_color = []
    lst_size = []
    for netobj, data in dct.items(): 
        lst.append(netobj)
        color = data.get(color_var)
        size = data.get(size_var)
        lst_color.append(color)
        lst_size.append(size)
    return lst, lst_size, lst_color
    
def extract_edgedict(dict_lst, var_lst, sort_var, reverse = True): 
    '''
    input:
        dict_lst: <list> list of dictionaries
        var_lst: <list> list of string
        sort_var: <string> var to sort by

    assumes: 
        len(dict_lst) == len(var_lst)

    returns: 
        sorted dictionary of edge data
    '''

    edge_dict = defaultdict(dict)
    for d, name in zip(dict_lst, var_lst): # you can list as many input dicts as you want here
        for key, value in d.items():
            edge_dict[key][name] = value
    edge_dict = dict(edge_dict)
    edge_dict_sorted = dict(sorted(edge_dict.items(), key = lambda x: x[1][sort_var], reverse = reverse))
    return edge_dict_sorted 

#### plot 1 ####
def plot_network(
    G, # <networkx.digraph>
    nodelst, # list of nodes (to control order of drawing)
    edgelst, # list of edges (to control order of drawing)
    color_dct, # color dictioanry
    label_dct, # label dictionary,
    query1, # first query 
    query2, # second query
    node_color, # <list/str> color of nodes 
    nodeedge_color, # <list/str> color of edges of nodes (outline)
    edge_color, # <list/str> color of edges
    node_size_lst, # <list> size of nodes (before scaling)
    edge_width_lst, # <list> width of edges (before scaling)
    node_divisor, # <float/int> scaling of node size 
    edge_divisor, # <float/int> scaling of edge width
    title, # <str> if any title 
    filename, # <str> for saving
    outfolder, # <str> for saving
    nlabels, # <int> number of labels (for logging)
    method, # <str> for logging 
    threshold, # <int/float> for logging
    seed, # <int> for reproducibility
    k = None, # <float> apply extra spacing between nodes (for visual purposes)
    nudge_triple = False, # nudge nodes for visual purposes 
    labeldict = None, # label dictionary 
    GCC = False, # for logging
    reverse = False # for logging
    ): 

    '''
    G: <networkx.classes.digraph.DiGraph> the graph
    node_size_lst: <list> node sizes 
    edge_width_lst: <list> edge width
    node_divisor: <int/float> scaling for all node sizes 
    edge_divisor: <int/float> scaling for all edges 
    title: <str> plot title 
    filename: <str> filename 
    '''

    # setup 
    fig, ax = plt.subplots(figsize=(8, 8), dpi=300, facecolor='w', edgecolor='k')
    plt.axis("off")

    # position & manual tweaking
    if k: 
        pos = nx.spring_layout(
            G = G, 
            k = k, 
            iterations = 30, 
            seed = seed)
    else: 
        pos = nx.spring_layout(
            G = G,
            seed = seed
        )

    if nudge_triple: 
        pos = nudge_position(pos, nudge_triple)

    # set up 
    node_size = [x/node_divisor for x in node_size_lst]
    #edge_width =  [x/edge_divisor if x > 50 else 0 for x in edge_width_lst] # NB: added cut-off for edges
    edge_width = [x/edge_divisor for x in edge_width_lst]

    # draw it 
    nx.draw_networkx_nodes(
        G, 
        pos, 
        nodelist = nodelst, 
        node_size = node_size, 
        node_color = node_color, 
        edgecolors = nodeedge_color, 
        linewidths = 0.5) #, node_size = node_size, node_color = node_color)

    nx.draw_networkx_edges(
        G, 
        pos, 
        edgelist = edgelst, 
        width = edge_width, 
        alpha = 0.5, 
        edge_color = edge_color, 
        arrows=False)

    # labels 
    labels = 'False'

    if labeldict: 

        label_options = {
            "edgecolor": "none", 
            "facecolor": "white", 
            "alpha": 0}

        nx.draw_networkx_labels(
            G, 
            pos, 
            labels = labeldict,
            font_size = 3, #10, 
            bbox = label_options,
            font_weight = 'bold')

        labels = 'True'
    
    # legend 
    lines, labels = get_legend(node_size, color_dct, label_dct, query1, query2)

    fig.legend(
        lines, 
        labels, 
        #loc = 'lower left', 
        labelspacing = 1, 
        fontsize = 15, 
        frameon = False)

    # save 
    plt.suptitle(f'{title}', size = 50)
    plt.tight_layout()
    plt.savefig(f"{outfolder}/{filename}_seed{seed}_k{k}_method{method}_threshold{threshold}_GCC{GCC}_labels{nlabels}_reverse{reverse}.pdf", bbox_inches='tight')

# main 
def main(inpath, outpath, query1, query2, method, thresholds, nlabels, GCC): 

    ''' 1. vars '''
    # basic vars
    seed = 11
    k = None 
    reverse = False
    source = "src"
    target = "trg"
    weight = "nij"
    focus_handles = None
    ## could be taken out !! ## 
    #focus_handles = [
    #    'zerdeve',
    #    'o_guest',
    #    'IrisVanRooij',
    #    'Kirstie_j',
    #    'briandavidarp',
    #    'BrianNosek',
    #    'siminevazire',
    #]
    
    
    # dictionaries 
    ## labels 
    dct_labels = {
        'openscience': 'Open Science',
        'replicationcrisis': 'Replication Crisis',
        'bropenscience': 'Bropenscience'
    }

    ## colors: https://colorbrewer2.org/#type=qualitative&scheme=Dark2&n=3
    c_node = { 
        f'{query1}': '#1b9e77', 
        f'{query2}': '#7570b3',
        'Overlap': "#d95f02"} 
    
    ## slightly darker for node-edge. 
    c_nodeedge = {
        f'{query1}': '#0b8560',
        f'{query2}': '#555094',
        'Overlap': '#b54e00'
    }

    # read node data
    df_nodedata = pd.read_csv(f"{inpath}/{query1}_{query2}_query.csv") # d_clean

    # gather thresholds 
    print(f"--> looping over thresholds:")
    for threshold in thresholds: 
        
        print(f"----> threshold: {threshold}")
        
        # read edgedata
        df_edgelist = pd.read_csv(f"{inpath}/{query1}_{query2}_bb_{method}_threshold{threshold}.csv") # df

        ## divisors 
        max_edge, max_node = get_maximum(df_edgelist, source, target, weight) 
        node_divisor = max_node / 500 # (2) max_node / (max_node/2)
        edge_divisor = max_edge / 2 # (10) max_edge / (max_edge/10)

        # create network
        G = nx.from_pandas_edgelist(
            df_edgelist, 
            source = source,
            target = target,
            edge_attr = weight
            )

        # log information
        G_nodes = len(G.nodes())
        G_edges = len(G.edges())
        print(f"nodes in G: {G_nodes}")
        print(f"edges in G: {G_edges}")

        # weighted degree
        degree_information(G, G.degree(weight = weight), "weighted_degree")

        # only GCC
        if GCC == "True": 
            largest_cc = max(nx.connected_components(G), key=len)
            G = G.subgraph(largest_cc)
            GCC_nodes = len(G.nodes())
            GCC_edges = len(G.edges())
            GCC_done = "yes"
            print(f"nodes in GCC: {GCC_nodes}")
            print(f"edges in GCC: {GCC_edges}")
        else: 
            GCC_nodes = G_nodes
            GCC_edges = G_edges 
            GCC_done = "no"

        ''' 3. create and set node attributes '''
        print('--> adding node & edge attributes')

        # mentions for color 
        d_query = dict(zip(df_nodedata["user"], df_nodedata["query"]))
        nx.set_node_attributes(G, d_query, "query")

        # size based on various kinds of degree 
        degree_information(G, G.degree(weight = weight), "weighted_degree_sub")
    
        ''' 4. create / set edge attributes '''
        # edge color 
        for i, j in G.edges():
            i_cat = G.nodes[i]["query"]
            j_cat = G.nodes[j]["query"]

            if i_cat == "Overlap" or j_cat == "Overlap": 
                edge_col = c_node.get("Overlap") # temporary

            else: 
                edge_col = 'tab:grey'

            G[i][j]['color'] = edge_col

        ''' 5. sort node dictionaries '''
        # different sorts 
        dct_node = dict(G.nodes(data=True))
        dct_weighted = sort_dictionary(dct_node, "weighted_degree_sub", reverse = reverse)

        ''' 6. extract values from node dictionaries '''
        # extract node values 
        nodelst_weighted, nodesize_weighted, nodecategory_weighted = extract_values(dct_weighted, "query", "weighted_degree_sub")

        ''' 6.1. category --> color '''
        nodecolor_weighted, nodeedgecolor_weighted = add_color(c_node, c_nodeedge, nodecategory_weighted)

        ''' 7. prepare edge dictionary '''
        # prepare edge dictionary
        edgeattr_color = nx.get_edge_attributes(G, 'color')
        edgeattr_weight = nx.get_edge_attributes(G, weight)
        edge_dict_list = [edgeattr_color, edgeattr_weight]
        edge_var_list = ['color', weight]
        dct_edge = extract_edgedict(edge_dict_list, edge_var_list, weight, reverse = reverse)

        ''' 8. extract values from edge dictionary '''
        edgelst, edgesize, edgecolor = extract_values(dct_edge, "color", weight)
        
        ## labels ---> next step 
        labeldict_weighted = get_labels(G, 'weighted_degree_sub', nodesize_weighted, nlabels, focus_handles = focus_handles)

        ''' plot weighted degree '''
        ## weighted degree 
        print('--> generating weighted degree plot')
        title = ''
        filename = f'{query1}_{query2}'
        nudge_triple = ""

        # plot 
        plot_network(
            G = G, 
            nodelst = nodelst_weighted,
            edgelst = edgelst,
            color_dct = c_node,
            label_dct = dct_labels, # label dictionary,
            query1 = query1, # first query 
            query2 = query2, # second query
            node_color = nodecolor_weighted,
            nodeedge_color = nodeedgecolor_weighted,
            edge_color = edgecolor,
            node_size_lst = nodesize_weighted, 
            edge_width_lst = edgesize,
            node_divisor = node_divisor,
            edge_divisor = edge_divisor,
            title = title,
            filename = filename,
            outfolder = outpath,
            nlabels = nlabels,
            method = method,
            threshold = threshold,
            k = k,
            seed = seed,
            nudge_triple = nudge_triple,
            labeldict = labeldict_weighted,
            GCC = GCC,
            reverse = reverse)

    ''' save logged information '''
    d = pd.DataFrame({
        'G_nodes': [G_nodes],
        'G_edges': [G_edges],
        'GCC_done': [GCC_done],
        'GCC_nodes': [GCC_nodes],
        'GCC_edges': [GCC_edges]
    })

    d.to_csv(f"{outpath}/{query1}_{query2}_seed{seed}_k{k}_method{method}_threshold{threshold}_GCC{GCC}_labels{nlabels}_reverse{reverse}.csv", index = False)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--inpath", required = True, type = str, help = "path to input folder (edgelist_simple)")
    ap.add_argument("-o", "--outpath", required = True, type = str, help = "path to output folder (for pdfs)")
    ap.add_argument("-q1", "--query1", required = True, type = str, help = "query, e.g. openscience")
    ap.add_argument("-q2", "--query2", required = True, type = str, help = "query, e.g. openscience")
    ap.add_argument("-m", "--method", required = True, type = str, help =  "which method to use (e.g. nc or df)")
    ap.add_argument("-t", "--thresholds", required = True, type = float, nargs = "+", help = "thresholds (float, list)")
    ap.add_argument("-n", "--nlabels", required = True, type = int, help = "how many labels to display")
    ap.add_argument("-g", "--gcc", required=False, type=str, default="True", help="subset dates (True) or not (False)")
    args = vars(ap.parse_args())

    main(
        inpath = args["inpath"],
        outpath = args["outpath"],
        query1 = args["query1"],
        query2 = args["query2"],
        method = args["method"],
        thresholds = args["thresholds"],
        nlabels = args["nlabels"],
        GCC = args["gcc"]
    )