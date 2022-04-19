"""
vmp 12-10-21: 
idea is to prune the graph, add W - 
and community to the graph & then save the .csv file. 
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

def main():

    ap = argparse.ArgumentParser(description="[INFO] ...")
    ap.add_argument("-m", "--matrix", required=True, help="path to matrix W")
    args = vars(ap.parse_args())

    fname = f'{"_".join(args["matrix"].split("_")[:-1])}.csv'

    #fpath = os.path.join("dat", "mettef_reopen_v2_norm_W.txt")
    W = np.loadtxt(args["matrix"])

    print("pairwise distance")
    D = pairwise_distances(W, metric="cosine")
    print(D.shape)

    # prune
    print("pruning D") # takes some time (a lot with the big one).
    D = dist_prune(D, w=3) # 2.2 original.
    idxs = list()

    ## remove no relations
    print("deleting from D")
    for (i, d) in enumerate(D):
        if np.sum(d) == 0.:
            idxs.append(i)
    D = np.delete(D, idxs, axis=0)
    D = np.delete(D, idxs, axis=1)
    print(D.shape)

    # update data by removing zero-relation messages

    data = pd.read_csv(fname)
    
    ## add max latent variable index
    print("W max")
    data["W_max"] = np.argmax(W, axis=1)
    data.drop(idxs,0,inplace=True)

    print("creating G") # takes some time (couple of minutes))
    G = nx.from_numpy_matrix(D) # potentially, we can use this without creating a graph.
    #pos = graphviz_layout(G)
    nx.write_gml(G, f'{fname.split(".")[0]}_G.gml')

    # community detection
    np.random.seed(seed=1234)
    print("community detection") # takes some time.
    parts = community_louvain.best_partition(G)

    # add community to data
    print("adding to data")
    data["graph_id"] = list(parts.keys())
    data["graph_community"] = list(parts.values())

    data.to_csv(f'{fname.split(".")[0]}_nmf.csv', index=False)

if __name__=="__main__":
    main()