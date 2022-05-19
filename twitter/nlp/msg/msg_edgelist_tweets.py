"""
vmp 12-10-21: 
idea is to prune the graph, add W - 
and community to the graph & then save the .csv file. 

BECOMES THE MAIN FILE FOR GRAPH PREPARATION

TODO: 
* igraph for speed
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
import igraph as ig
import time
from tqdm import tqdm
import gc

def dist_prune(delta, w = 2):
    """ prune matrix by removing edges that have a distance larger
        than condition cond (default mean distance)
    """
    cond = np.mean(delta) - w * np.std(delta)
    #total = range(delta.shape[0])
    #print(f"total: {total}")
    for i in range(delta.shape[0]):
        if i%1000 == 0: 
            print(i)
        for j in range(delta.shape[1]):
            val = delta[i, j]
            if val > cond:
                delta[i, j] = 0
            else:
                delta[i, j] = delta[i, j]

    return delta

def main(infile_csv, infile_W, outpath, textcol, prune):

    print("--- starting: nmf ---")

    # load W file
    print("--> loading data")
    W = np.loadtxt(infile_W)

    print("--> pairwise distances")
    D = pairwise_distances(W, metric="cosine") # W.T perhaps for opposite
    print(D.shape)

    print("--> calculate cond")
    cond = np.mean(D) - prune * np.std(D)
    print(f"cond = {cond}")
    print("--> insert 0")
    D[D > cond] = 0 # probably smarter (distance, so larger than!)

    ## still this 
    print("--> idxs")
    idxs = list()
    for (i, d) in enumerate(D):
        if i%1000 == 0: 
            print(i)
        if np.sum(d) == 0.:
            idxs.append(i)
    print(f"len idx: {len(idxs)}")

    #D = np.delete(D, idxs, axis=0) # this is actually the crazy part
    #D = np.delete(D, idxs, axis=1)

    ## update data
    print("--> csv & w max")
    data = pd.read_csv(infile_csv)
    data = data[~data[textcol].isnull()]
    data = data.reset_index(drop = True) # need to validate this somehow
    print(f"{len(data)}")

    ## add max latent variable index
    print("--> W max")
    data["W_max"] = np.argmax(W, axis=1)
    data["W_val"] = np.max(W, axis=1)
    data.drop(idxs, 0, inplace=True)
    data["index"] = data.index

    ## save data 
    print(f"--> writing W max dataframe")
    outname = re.search("topic_model/(.*)_W.txt", infile_W)[1]
    data.to_csv(f'{outpath}{outname}_prune{prune}_nmf.csv', index=False)

    ## get distance
    distance = D[D != 0] # should give me the same?
    distance = pd.DataFrame(distance, columns = ["dist"]) # pretty fast 

    ## sources, targets
    print("--> sources, targets")
    sources, targets = D.nonzero() # fine

    ## edgelist
    print("--> df edgelist")
    df_edgelist = pd.DataFrame(
        zip(sources.tolist(), targets.tolist()),
        columns = ["src", "trg"])

    ## concat ---> here we fuck it up actually I think
    print("--> concatenate stuff")
    df_edgelist = pd.concat([df_edgelist.reset_index(drop=True), distance.reset_index(drop=True)], axis=1) # fast

    ## save edgeslist 
    print("--> write edgelist file")
    df_edgelist.to_csv(f"{outpath}{outname}__prune{prune}_edgelist.csv", index = False) # what takes longest...
    

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
        textcol = args["textcol"],
        prune = args["prune"])
