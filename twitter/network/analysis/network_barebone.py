import pandas as pd 
import numpy as np
import re
import networkx as nx 
import matplotlib.pyplot as plt 

# load file 
df = pd.read_pickle("/work/50114/twitter/data/network/df_edgelist.pkl")  

# weighted, ignoring differences. 
df = df.groupby(['from', 'to']).size().to_frame('weight').reset_index().sort_values('weight', ascending=False)
df.head(5)

# networkx 
G = nx.from_pandas_edgelist(df,source='from',target='to', edge_attr='weight', create_using=nx.DiGraph())

#### edge attributes ####

# width by weight
edge_weights = nx.get_edge_attributes(G, 'weight').values() 
max_width = max(edge_weights)

#### node attributes ####

# size by degree
degrees = {node:val for (node, val) in G.degree()}
nx.set_node_attributes(G, degrees, "degree")
degree_data = nx.get_node_attributes(G, 'degree').values()

#### plot ####
pos = nx.spring_layout(G, seed=8)

# setup 
fig, ax = plt.subplots(figsize=(12, 12), dpi=200, facecolor='w', edgecolor='k')
plt.axis("off")

# set up 
node_size = [node_degree/20 for node_degree in degree_data]
edge_width =  [edge_weight/50 for edge_weight in edge_weights]

# draw it 
nx.draw_networkx_nodes(G, pos, node_size=node_size) #, node_size = node_size, node_color = node_color)
nx.draw_networkx_edges(G, pos, width = edge_width, alpha = 0.5) #, edge_color = edge_col)