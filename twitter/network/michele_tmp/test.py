import backboning
import pandas as pd
import os
import networkx as nx

toy_table = pd.read_csv("fig3/toy_net", sep = "\t")

## create network
G = nx.from_pandas_edgelist(
    toy_table, 
    source = "src",
    target = "trg",
    edge_attr = "nij"
    )

## add degree
degree = {node:val for (node, val) in G.degree(weight = "nij")}
degree_lst = list(degree.values())
nx.set_node_attributes(G, degree, "degree")

## extract weight
edge_weight = nx.get_edge_attributes(G, 'nij')
weight_lst = list(edge_weight.values())

pos = nx.spring_layout(G)
nx.draw_networkx_nodes(G, pos, node_size = [x*10 for x in degree_lst])
nx.draw_networkx_edges(G, pos, width = weight_lst)

## their preprocessing 
table_nc = backboning.noise_corrected(toy_table, undirected = True)
table_df = backboning.disparity_filter(toy_table, undirected = True)

bb_neffke = backboning.thresholding(table_nc, 4)
bb_vespignani = backboning.thresholding(table_df, 0.66)

bb_neffke
bb_vespignani


