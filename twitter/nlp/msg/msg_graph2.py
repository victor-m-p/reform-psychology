"""


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


# this is where we need to change.
def dist_prune(delta, w = 2): 
    """ prune matrix by removing edges that have a distance larger
        than condition cond (default mean distance)
        larger w = 
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
    
    ## testing some stuff 
    print(f'fname: {fname}')
    print(f'args: {args["matrix"]}')

    #fpath = os.path.join("dat", "mettef_reopen_v2_norm_W.txt")
    W = np.loadtxt(args["matrix"])

    D = pairwise_distances(W, metric="cosine")
    print(D.shape)
    # prune
    D = dist_prune(D, w=2.2) # orig
    idxs = list()
    ## remove no relations
    for (i, d) in enumerate(D):
        if np.sum(d) == 0.:
            idxs.append(i)
    D = np.delete(D, idxs, axis=0)
    D = np.delete(D, idxs, axis=1)
    print(D.shape)
    
    
    # update data by removing zero-relation messages
    data = pd.read_csv(fname)
    ## add max latent variable index
    data["W_max"] = np.argmax(W, axis=1)
    data.drop(idxs,0,inplace=True)
    
    G = nx.from_numpy_matrix(D)

    '''
    # get largest connected component 
    Gcc = sorted(nx.connected_components(G), key=len, reverse=True)
    G = G.subgraph(Gcc[0])
    '''

    pos = graphviz_layout(G)
    # community detection
    np.random.seed(seed=1234)
    parts = community_louvain.best_partition(G)
    
    # add community to data (just commented out)
    #data["graph_id"] = list(parts.keys())
    #data["graph_community"] = list(parts.values())
    
    values = [parts.get(node) for node in G.nodes()]

    # degrees
    deg = nx.degree(G)
    keys = [t[0] for t in deg]
    ## weight node size by degrees
    degvalues = [t[1] for t in deg]
    ## weight node size by engagement
    #engagement = [int(f+1) for f in data["engagement"].values] ### just commented out ###
    binaryHit = [1 if x > 1 else 0 for x in data["nHits"]]
    continuousHit = [x for x in data["nHits"]]
    continuousCom = [x for x in data["nCom"]]

    #print(engagement)
    # add max topic as node name
    #wmax = data["W_max"].values
    #labels = dict(zip(keys, wmax))
    
    # color = hit keywords or not, 
    # size = number of comments. 
    plt.figure(figsize=(15, 15), dpi=150, facecolor='w', edgecolor='k')
    plt.axis("off")
    nx.draw_networkx(
        G, 
        pos=pos, 
        cmap=plt.get_cmap("tab20"), 
        node_color=binaryHit,
        #node_size=200, 
        #font_size=8, 
        width=.02, 
        #font_weight="bold",
        #font_color="k", 
        alpha=0.8, 
        edge_color="gray",
        #nodelist=keys,
        node_size=continuousCom, ### just commented out ###
        with_labels=False
        )
    plt.tight_layout()
    plt.savefig(f'fig/{os.path.basename(fname).split(".")[0]}_col_HitB_size_ComN.png')
    plt.close()


    # color = hit keywords or not
    # size = how many keywords (nonbinary)
    plt.figure(figsize=(15, 15), dpi=150, facecolor='w', edgecolor='k')
    plt.axis("off")
    nx.draw_networkx(
        G, 
        pos=pos, 
        cmap=plt.get_cmap("tab20"), 
        node_color=binaryHit,
        #node_size=200, 
        #font_size=8, 
        width=.02, 
        #font_weight="bold",
        #font_color="k", 
        alpha=0.8, 
        edge_color="gray",
        #nodelist=keys,
        node_size=[x*100 if x > 1 else 20 for x in data["nHits"]], ### just commented out ###
        with_labels=False
        )
    plt.tight_layout()
    plt.savefig(f'fig/{os.path.basename(fname).split(".")[0]}_col_HitB_size_HitC.png')
    plt.close()

    '''
    # graph with message id as node label
    plt.figure(figsize=(15, 15), dpi=150, facecolor='w', edgecolor='k')
    plt.axis("off")
    nx.draw_networkx(
        G, 
        pos=pos, 
        cmap=plt.get_cmap("tab20"), 
        node_color=continuousHit,
        #node_size=200, 
        #font_size=8, 
        width=.5, 
        #font_weight="bold",
        #font_color="k", 
        alpha=0.8, 
        edge_color="gray",
        #nodelist=keys,
        node_size=continuousCom, ### just commented out ###
        with_labels=False
        )
    plt.tight_layout()
    plt.savefig(f'fig/{os.path.basename(fname).split(".")[0]}_continuousHit_noLab.png')
    plt.close()

'''
    # color = hit keywords or not (binary)
    # size = hit keywords or not (binary)
    plt.figure(figsize=(15, 15), dpi=150, facecolor='w', edgecolor='k')
    plt.axis("off")
    nx.draw_networkx(
        G, 
        pos=pos, 
        cmap=plt.get_cmap("tab20"), 
        node_color=binaryHit,
        #labels = labels,
        #node_size=200, 
        #font_size=8, 
        width=.02, 
        #font_weight="bold",
        #font_color="k", 
        alpha=1, 
        edge_color="gray",
        #nodelist=keys,
        node_size=[300 if x > 1 else 20 for x in data["nHits"]], ## just commented out
        with_labels=False
        )
    plt.tight_layout()
    plt.savefig(f'fig/{os.path.basename(fname).split(".")[0]}_col_HitB_size_HitB.png')
    plt.close()

    # graph with max W id as node label
    plt.figure(figsize=(15, 15), dpi=150, facecolor='w', edgecolor='k')
    plt.axis("off")
    nx.draw_networkx(
        G, 
        pos=pos, 
        cmap=plt.get_cmap("tab20"), 
        node_color=values,
        #labels = labels,
        #node_size=200, 
        #font_size=8, 
        width=.02, 
        #font_weight="bold",
        #font_color="k", 
        alpha=1, 
        edge_color="gray",
        #nodelist=keys,
        node_size=[300 if x > 1 else 20 for x in data["nHits"]], ## just commented out
        with_labels=False
        )
    plt.tight_layout()
    plt.savefig(f'fig/{os.path.basename(fname).split(".")[0]}_col_Community_size_hitB.png')
    plt.close()

    # graph with max W id as node label
    plt.figure(figsize=(15, 15), dpi=150, facecolor='w', edgecolor='k')
    plt.axis("off")
    nx.draw_networkx(
        G, 
        pos=pos, 
        cmap=plt.get_cmap("tab20"), 
        node_color=values,
        #labels = labels,
        #node_size=200, 
        #font_size=8, 
        width=.02, 
        #font_weight="bold",
        #font_color="k", 
        alpha=0.8, 
        edge_color="gray",
        #nodelist=keys,
        node_size=continuousCom, ## just commented out
        with_labels=False
        )
    plt.tight_layout()
    plt.savefig(f'fig/{os.path.basename(fname).split(".")[0]}_col_Community_size_ComN.png')
    plt.close()

    #data.to_csv(f'{fname.split(".")[0]}_nmf.csv', index=False) (just commented out)

if __name__=="__main__":
    main()

