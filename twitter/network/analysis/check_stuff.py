'''
VMP 2022-04-14: 
Check the networks manually.
'''

# imports 
import networkx as nx 
import pandas as pd 

## load stuff
df_edgelist = pd.read_csv("/work/50114/twitter/data/network/testing/replicationcrisis_openscience_cutoff30_edgelist.csv")
df_nodedata = pd.read_csv("/work/50114/twitter/data/network/testing/replicationcrisis_openscience_cutoff30_nodedata.csv")

# create G 
G = nx.from_pandas_edgelist(
    df_edgelist, 
    source = "username_from",
    target = "username_to",
    edge_attr = "weight"
    )

# assign weighted degree to all the nodes 
degree = {node:val for (node, val) in G.degree(weight='weight')}
nx.set_node_attributes(G, degree, "weighted_degree")

# sorted degree (what we should probably subset actually...)
degree_sort = sorted(degree.items(), key=lambda x: x[1], reverse=True)
df_degree = pd.DataFrame(
    degree_sort, columns = ['id', 'degree_w']
)
df_degree.head(20)

## how different is it if we subset the other way? ##
df_sub = df_edgelist[df_edgelist["weight"] > 30]
G0 = nx.from_pandas_edgelist(
    df_sub, 
    source = "username_from",
    target = "username_to",
    edge_attr = "weight"
    )

degree0 = {node:val for (node, val) in G0.degree(weight='weight')}
nx.set_node_attributes(G0, degree, "weighted_degree")
degree_sort0 = sorted(degree0.items(), key=lambda x: x[1], reverse=True)
df_degree0 = pd.DataFrame(
    degree_sort0, columns = ['id', 'degree_w']
)
df_degree0.head(20)

## deselect nodes with less than e.g. 50 degree ## 
selected_nodes = [n for n,v in G.nodes(data=True) if v['weighted_degree'] > 50]  
H = G.subgraph(selected_nodes)

len(G.nodes())
len(H.nodes())

## cannot find ## 
# -->  lfryoona 
# --> BrianNosek
# --> AllenInstitute 
# --> ... more 



# read networks 
data = pd.DataFrame({
    'from': ['a', 'b', 'c'],
    'to': ['b', 'c', 'd'],
    'weight': [1, 2, 3]
})

data.dtypes

G = nx.from_pandas_edgelist(
        data, 
        source = "from",
        target = "to",
        edge_attr = "weight"
        )

G.nodes['a']['label'] = 'first'
G.nodes['b']['label'] = 'second'
G.nodes['c']['label'] = 'third'
G.nodes['d']['label'] = 'forth'

G.edges['a', 'b']["test"] = "best"
G['b']['c']['test'] = 'best'

path = "/work/50114/twitter/data/network/networks/"
# write graph (testing)
nx.write_gml(G, f"{path}test.gml")
nx.write_graphml(G, f"{path}test.graphml")


G = nx.read_gml(f"{path}test.gml")
G = nx.read_graphml(f"{path}test.graphml")
G.nodes(data=True)
G.edges(data=True)

G2 = nx.read_graphml("/work/50114/twitter/data/network/networks/replicationcrisis_openscience_cutoff30.graphml")

G1.nodes(data=True)
G1.edges(data=True) # have weight. 