'''
VMP 2022-04-19: 
test igraph (for speed).
'''

#import igraph as ig 
import networkx as nx
import pandas as pd 
import numpy as np
from sklearn.metrics import pairwise_distances
from timeit import default_timer as timer


## test something else ##
W = np.loadtxt("/work/50114/twitter/data/nlp/msg/topic_model/os_rc_5_typeretweet_k100_W.txt")
data = pd.read_csv("/work/50114/twitter/data/nlp/by_tweet/os_rc_5_typeretweet.csv")
data = data[~data["clean_lemma"].isnull()]
data = data.reset_index(drop = True)

len(data)
len(data)

data[data.index == 18901]


node_names = ['A', 'B', 'C']
a = pd.DataFrame([[1,2,3],[3,1,1],[4,0,2]], index=node_names, columns=node_names)

# Get the values as np.array, it's more convenenient.
A = a.values
A[A < 2] = 0 


w = 1
cond = np.mean(A) - w * np.std(A)

### test something ###
topics = ['A', 'B', 'C']
tweets = [1, 2, 3, 4, 5]
a = pd.DataFrame([
    [0.2, 0.4, 0.4],
    [0.2, 0.4, 0.4],
    [0.3, 0.5, 0.2],
    [0.5, 0.3, 0.2],
    [0.8, 0.1, 0.1]], 
    index=tweets, 
    columns=topics)
A = a.values

# AT 
AT = A.T
DT = pairwise_distances(AT, metric="cosine")
DT

# normalize (broadcasting)
row_sums = AT.sum(axis=1)
new_matrix = AT / row_sums[:, np.newaxis]
new_matrix

DT2 = pairwise_distances(new_matrix, metric = "cosine") 
## automatically normalizes --> so we probably have to scale
## we can probably do this by how "large" the topics are overall 



D = pairwise_distances(A, metric="cosine") # it is distance actually, wow.
w = 1
cond = np.mean(D) - w * np.std(D)

# set them to zero
D[D > 0.1] = 0
print(D.shape)

# need at least idxs
idxs = list()
for (i, d) in enumerate(D):
    if np.sum(d) == 0.:
        idxs.append(i)

# save indexes that are completely deleted 

## get edgelist
sources, targets = D.nonzero()
edgelist = list(zip(sources.tolist(), targets.tolist()))

pd.DataFrame(
    zip(sources.tolist(), targets.tolist()),
    columns = ["A", "B"])

## get distance
distance = D[D != 0]

## put it together
df_edgelist = pd.DataFrame(edgelist, columns = ["src", "trg"])
df_distance = pd.DataFrame(distance, columns = ["dist"])
df_distance = df_c = pd.concat([df_edgelist.reset_index(drop=True), df_distance.reset_index(drop=True)], axis=1)


# their approach

idxs = list()
for (i, d) in enumerate(D):
    print(i)
    if np.sum(d) == 0.:
        idxs.append(i)
D = np.delete(D, idxs, axis=0)
D = np.delete(D, idxs, axis=1)

print(D.shape)

D



# actually delete the zeros 
D_del = D[D > 0.001]
print(D_del.shape)

# 
for (i, d) in enumerate(D):
        if np.sum(d) == 0.:
            idxs.append(i)
    D = np.delete(D, idxs, axis=0)
    D = np.delete(D, idxs, axis=1)



g = ig.Graph.Weighted_Adjacency(A.tolist())
g_one = g.get_edge_dataframe().reset_index().drop(columns = 'edge ID')


# Create graph, A.astype(bool).tolist() or (A / A).tolist() can also be used.
g = ig.Graph.Adjacency((A > 0).tolist())
g.es['weight'] = A[A.nonzero()]

## this is the thing
perfect = g.get_edge_dataframe().reset_index().drop(columns = 'edge ID')

## test speed 
G = nx.read_gml("/work/50114/twitter/data/nlp/msg/bropenscience_tweet_text_stopwords_k15_G.gml", destringizer=int) # takes some time to load
G.edges(data=True)


# import file
## NB: why is this so fucked??
## infile_W = "/work/50114/twitter/data/nlp/msg/replicationcrisis_tweet_text_stopwords_k15_W.txt" 
infile_W = "/work/50114/twitter/data/nlp/msg/openscience_replicationcrisis_intersection_tweet_text_k15_W.txt"
W = np.loadtxt(infile_W)
D = pairwise_distances(W, metric = "cosine")
print(D.shape)

# subset for now (check whether we can brute force it though or do something smart)
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

D_prune = dist_prune(D, w = 2)
print(D_prune.shape)

# remove self-loops: 
for (i, d) in enumerate(D_prune):
    if np.sum(d) == 0.:
        idxs.append(i)
D_prune = np.delete(D, idxs, axis=0)
D_prune = np.delete(D, idxs, axis=1)
print(D_prune.shape)

# igraph 
start_ig = timer()
#A = W.values
g = ig.Graph.Adjacency((D > 0).tolist())
g.es['weight'] = D[D.nonzero()]
igraph_edgelist = g.get_edge_dataframe().reset_index().drop(columns = 'edge ID')
end_ig = timer() 



start_nx = timer()
G = nx.from_numpy_matrix(D) # potentially not creating a graph
edgelist = nx.to_pandas_edgelist(G)
end_nx = timer()

end_ig - start_ig

igraph_edgelist.to_csv("/work/50114/twitter/data/nlp/msg/openscience_intersection_tmp.csv", index = False)
