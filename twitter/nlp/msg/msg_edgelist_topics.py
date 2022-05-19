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


def main(infile, outpath):

    print("--- starting: edgelist semantic ---")

    # load W file
    print("--> loading data")
    W = np.loadtxt(infile)
    print(f"W shape: {W.shape}")

    # transpose W
    print("--> transposing W")
    WT = W.T
    print(f"W.T shape: {WT.shape}")

    # pairwise distance
    print("--> pairwise distances")
    D = pairwise_distances(WT, metric="cosine")
    print(f"D shape: {D.shape}")

    ## get distance
    print(f"--> adding distance")
    distance = D[D != 0]
    distance = pd.DataFrame(distance, columns = ["dist"]) # pretty fast 

    ## sources, targets
    print("--> sources, targets")
    sources, targets = D.nonzero() # fine

    ## edgelist
    print("--> df edgelist")
    df_edgelist = pd.DataFrame(
        zip(sources.tolist(), targets.tolist()),
        columns = ["src", "trg"])

    ## concat
    print("--> concatenate stuff")
    df_edgelist = pd.concat([df_edgelist.reset_index(drop=True), distance.reset_index(drop=True)], axis=1) # fast

    ## save edgeslist 
    print("--> write edgelist file")
    outname = re.search("topic_model/(.*)_W.txt", infile)[1]
    df_edgelist.to_csv(f"{outpath}{outname}_semantic_edgelist.csv", index = False) # writing 
    print(f"--- finished: edgelist semantic ---")

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--infile", required=True, type=str, help="inpath")
    ap.add_argument("-o", "--outpath", required=True, type=str, help="outpath")
    args = vars(ap.parse_args())

    main(
        infile = args["infile"], 
        outpath = args["outpath"]
    )
