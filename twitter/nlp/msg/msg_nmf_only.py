"""
vmp 12-10-21: 
idea is to prune the graph, add W - 
and community to the graph & then save the .csv file. 

BECOMES THE MAIN FILE FOR GRAPH PREPARATION
"""


import argparse
import os
import numpy as np
from sklearn.metrics import pairwise_distances
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
from community import community_louvain
import matplotlib.pyplot as plt
import pandas as pd
import itertools 
import re


def dist_prune(delta, w = 2):
    """ prune matrix by removing edges that have a distance larger
        than condition cond (default mean distance)
    """
    cond = np.mean(delta) - w * np.std(delta)
    for i in range(delta.shape[0]):
        for j in range(delta.shape[1]):
            val = delta[i, j]
            if val > cond:
                delta[i, j] = 0.
            else:
                delta[i, j] = delta[i, j]

    return delta

def main(infile_csv, infile_W, outpath, textcol, prune):

    # load W file
    W = np.loadtxt(infile_W)

    D = pairwise_distances(W, metric="cosine")
    print(D.shape)

    # prune
    D = dist_prune(D, w = prune) # prune = 2.2 (original)
    idxs = list()

    ## remove no relations
    for (i, d) in enumerate(D):
        if np.sum(d) == 0.:
            idxs.append(i)
    D = np.delete(D, idxs, axis=0)
    D = np.delete(D, idxs, axis=1)
    print(D.shape)

    # update data by removing zero-relation messages
    data = pd.read_csv(infile_csv)
    data = data[~data[textcol].isnull()]

    ## add max latent variable index
    print("W max")
    data["W_max"] = np.argmax(W, axis=1)
    data.drop(idxs, 0, inplace=True)

    # outfile 
    print("creating G") # takes some time (couple of minutes))
    G = nx.from_numpy_matrix(D) # potentially not creating a graph
    
    #pos = graphviz_layout(G)
    outname = re.search("msg/(.*)_W.txt", infile_W)[1]
    nx.write_gml(G, f'{outpath}{outname}_G.gml')

    # community detection
    np.random.seed(seed=1234)
    print("community detection") # takes some time.
    parts = community_louvain.best_partition(G) # best communities (but could also be in other file)

    # add community to data
    print("adding to data")
    data["graph_id"] = list(parts.keys())
    data["graph_community"] = list(parts.values())

    data.to_csv(f'{outpath}{outname}_nmf.csv', index=False)
    print(f"--- finished: nmf ---")

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-ic", "--infile_csv", required=True, type=str, help="path to csv")
    ap.add_argument("-iw", "--infile_W", required=True, type=str, help="path to folder for output csv")
    ap.add_argument("-o", "--outpath", required=True, type=str, help="outpath")
    ap.add_argument("-t", "--textcol", required=True, type=str, help="column name for text")
    ap.add_argument("-p", "--prune", required=True, type=float, help="pruning level (default: 2.2)")
    args = vars(ap.parse_args())

    main(
        infile_csv = args["infile_csv"], 
        infile_W = args["infile_W"], 
        outpath = args["outpath"],
        prune = args["prune"])
