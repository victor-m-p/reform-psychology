"""

"""
import argparse
import os
import pandas as pd
import re
import networkx as nx
from community import community_louvain
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt

def main():
    ap = argparse.ArgumentParser(description="[INFO] ...")
    ap.add_argument("-d", "--dataset", required=True, help="path to input dataset")
    args = vars(ap.parse_args())
    # extract user vars
    data = pd.read_csv(args["dataset"])
    usr = data["usr"].values
    usrid = data["usr_id"].values
    nodeid = data["node_id"].values
    # fix ids, for user ids some contain profile.php, use usr
    ## some users contain all comment users on user name
    ids = list()
    for (i, id) in enumerate(usrid):
        base = id.split("/")[-1]
        if ".php" in base:
            base = usr[i]
            tokens = base.split()
            for (j, token) in enumerate(tokens):
                r = re.findall('([A-Z])', token)
                if len(r) == 2:
                    base = " ".join(tokens[:j]) + " " + token.split(r[1])[0]
                    break
        ids.append(base)
    data["usr_id_norm"] = ids

    # descriptive comment level 0
    child0 = list()
    for id in nodeid:
        child0.append(id.split("_")[0])
    
    # comment frequency
    level0 = dict()
    for (i, id) in enumerate(ids):
        #level0[id] = child0[i]
        if id in level0.keys():
            level0[id] += 1
        else:
            level0[id] = 1
    
    
    df0 = pd.DataFrame.from_dict(level0, orient='index', columns=["n_posts"])
    df0 = df0.sort_values(by="n_posts", ascending=False)
    df0.reset_index(level=0, inplace=True)
    df0 = df0.rename(columns={"index": "usr"})
    print(f"INFO number of unique users {df0.shape[0]} and number of posts {data.shape[0]}")


    # Draw plot
    plt.figure(figsize=(15, 7), dpi=150, facecolor="w", edgecolor="k")
    plt.plot("usr", "n_posts", data=df0, color="red", linewidth=4)
    plt.xticks(rotation=70)
    plt.savefig("ncom_usr_dist.png")
    


    # TODO: function for bipartite graphs
    df = pd.DataFrame()
    df["usr_id_norm"] = ids
    df["childl0"] = [re.sub("comments", "C", child) for child in child0]
    df["W_max"] = data["W_max"].values
    #print(df)

    print(df.shape)
    idxs = df["usr_id_norm"] == ""
    df = df.loc[~idxs,:]
    print(df.shape)

    G = nx.Graph()
    G.add_nodes_from(df["usr_id_norm"], bipartite=0)
    G.add_nodes_from(df["childl0"], bipartite=1)
    G.add_weighted_edges_from(
        [(row["childl0"], row["usr_id_norm"], 1) for idx, row in df.iterrows()], 
        weight='weight')


    # degrees
    deg = nx.degree(G)
    keys = [t[0] for t in deg]
    ## weight node size by degrees
    degvalues = [t[1] for t in deg]
    

    #for d in deg:
    #    print(d)


    
  
    pos = graphviz_layout(G)

    parts = community_louvain.best_partition(G)
    values = [parts.get(node) for node in G.nodes()]
    plt.figure(figsize=(30, 30), dpi=150, facecolor='w', edgecolor='k')
    plt.axis("off")
    nx.draw(
        G, 
        pos=pos,
        cmap=plt.get_cmap("tab20"),
        node_color=values,
        with_labels=False,
        #node_size=300,
        width=.5,
        edge_color="gray",
        nodelist=keys,
        node_size=[v * 20 for v in degvalues]
        )
    ## bartite graph
    #for p in pos:  # raise text positions
    #    pos[p][1] += 0.25
    nx.draw_networkx_labels(G, pos, font_weight="bold")
    plt.tight_layout()
    plt.savefig("test_com_usr.png")
    
    ## comment-w_max bipartite graph
    G1 = nx.Graph()
    G1.add_nodes_from(df["W_max"], bipartite=0)
    G1.add_nodes_from(df["childl0"], bipartite=1)
    G1.add_weighted_edges_from(
        [(row["childl0"], row["W_max"], 1) for idx, row in df.iterrows()], 
        weight='weight')
    deg = nx.degree(G1)
    keys = [t[0] for t in deg]
    ## weight node size by degrees
    degvalues = [t[1] for t in deg]

    pos = graphviz_layout(G1)
    parts = community_louvain.best_partition(G1)
    values = [parts.get(node) for node in G1.nodes()]
    plt.figure(figsize=(30, 30), dpi=150, facecolor='w', edgecolor='k')
    plt.axis("off")
    nx.draw(
        G1, 
        pos=pos,
        cmap=plt.get_cmap("tab20"),
        node_color=values,
        with_labels=False,
        #node_size=300,
        width=.5,
        edge_color="gray",
        nodelist=keys,
        node_size=[v * 50 for v in degvalues]
        )
    nx.draw_networkx_labels(G1, pos, font_weight="bold")
    plt.tight_layout()
    plt.savefig("test_com_w.png")


    
    ## usr-w_max bipartite graph
    G2 = nx.Graph()
    G2.add_nodes_from(df["W_max"], bipartite=0)
    G2.add_nodes_from(df["usr_id_norm"], bipartite=1)
    G2.add_weighted_edges_from(
        [(row["usr_id_norm"], row["W_max"], 1) for idx, row in df.iterrows()], 
        weight='weight')
    deg = nx.degree(G2)
    keys = [t[0] for t in deg]
    ## weight node size by degrees
    degvalues = [t[1] for t in deg]

    print(dir(G2))

    print(nx.info(G2))


    pos = graphviz_layout(G2)
    parts = community_louvain.best_partition(G2)
    values = [parts.get(node) for node in G2.nodes()]
    plt.figure(figsize=(30, 30), dpi=150, facecolor='w', edgecolor='k')
    plt.axis("off")
    nx.draw(
        G2, 
        pos=pos,
        cmap=plt.get_cmap("tab20"),
        node_color=values,
        with_labels=False,
        #node_size=300,
        width=.5,
        edge_color="gray",
        nodelist=keys,
        node_size=[v * 50 for v in degvalues]
        )
    nx.draw_networkx_labels(G2, pos, font_weight="bold")
    plt.tight_layout()
    plt.savefig("test_usr_w.png")

if __name__=="__main__":
    main()