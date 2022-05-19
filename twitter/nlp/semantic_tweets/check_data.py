'''


'''
# imports
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
pd.set_option('display.max_colwidth', None)

# based just on count of max topic
d = pd.read_csv("/work/50114/twitter/data/nlp/msg/semantic_tweets/os_rc_5_typeretweet_k100_prune2.0_nmf.csv")
log_topics = "/work/50114/twitter/data/nlp/msg/topic_model/os_rc_5_typeretweet_k100_log.txt"
topics = pd.read_csv(log_topics, sep = ":", header = None, skiprows=2)
topics.columns = topics.columns = ["topic", "words"]
W = np.loadtxt("/work/50114/twitter/data/nlp/msg/topic_model/os_rc_5_typeretweet_k100_W.txt")
d_edgelst = pd.read_csv("/work/50114/twitter/data/nlp/msg/semantic_tweets/os_rc_5_typeretweet_k100__prune2.0_edgelist.csv")

d_edgelst = d_edgelst[d_edgelst["src"] < d_edgelst["trg"]]
d_edgelst = d_edgelst.sort_values("dist", ascending=True)

# topic similarity
## every tweet labelled by maximum & then connections 

## perhaps backboning for this as well 

## check something very CLOSE 
## check something very DISTANT
high = d_edgelst[d_edgelst["dist"] > 0.73]
low = d_edgelst[d_edgelst["dist"] == d_edgelst["dist"].min()]

high # very few with the same HIGH value?
low # crazy many with the same LOW value?

d[d.index == 8398]["clean_text"]
d[d.index == 14140]["clean_text"]

## check maximums 
def display_pair(d, src, trg):
    d_one = d[d.index == src]["clean_lemma"]
    d_two = d[d.index == trg]["clean_lemma"]
    print(f"src: {d_one} \n")
    print(f"trg: {d_two}")

## it is inverse (so we need to get inverse)
# just one minus? #
d_edgelst["weight"] = [1-x for x in d_edgelst["dist"]]
d_edgelst["weight"].min()
d_edgelst["weight"].max()

## assign max categories to src and trg
d["index"] = d.index

d_src = d.rename(columns = {
    'index': 'src',
    'W_max': 'W_src'
})[['src', 'W_src']]

d_trg = d.rename(columns = {
    'index': 'trg',
    'W_max': 'W_trg'
})[["trg", "W_trg"]]

len(d_edgelst)
d_edgelst_src = d_edgelst.merge(d_src, on = "src", how = "inner")
d_edgelst_src.head(5) 
len(d_edgelst_src) # a bit fewer --- weird (some index not there?)

d_edgelst_trg = d_edgelst_src.merge(d_trg, on = "trg", how = "inner")
len(d_edgelst_trg) # a bit fewer again (more fewer actually) 

d_topics_weight = d_edgelst_trg.groupby(['W_src', 'W_trg'])['weight'].sum().reset_index(name = 'weight')

### test what we have ###
d_max = d_topics_weight[d_topics_weight["weight"] > 35000]
d_min = d_topics_weight[d_topics_weight["weight"] < 100]

## check them 
def get_topic(d, t1, t2):
    w1 = d[d["topic"] == f"dimension-{t1}"][["words"]]
    w2 = d[d["topic"] == f"dimension-{t2}"][["words"]]
    print(f"topic {t1}: {w1} \n")
    print(f"topic {t2}: {w2}")


### max relation ###
get_topic(topics, 75, 70) # psychology, replication, crisis
get_topic(topics, 97, 80) # science, physics, bio
get_topic(topics, 97, 86) # bio, psychedelic

### minimum relation ###
get_topic(topics, 86, 33) # psychedelc vs. eu/infrastructure
get_topic(topics, 86, 75) # psychedelic vs. replication crisis
get_topic(topics, 97, 75) # bio and replication crisis

## create network
d_topics_weight.head(5)
G = nx.from_pandas_edgelist(
    d_topics_weight,
    source = "W_src",
    target = "W_trg",
    edge_attr = "weight"
)

## community detection
from community import community_louvain
G.edges(data=True)
