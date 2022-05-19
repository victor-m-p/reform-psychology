'''
VMP 2022-04-25:
label topics (used for both "topics" & "tweets")
'''

# imports
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from community import community_louvain
import re
pd.set_option('display.max_colwidth', None)

# based just on count of max topic
log_topics = "/work/50114/twitter/data/nlp/msg/topic_model/os_rc_5_typeretweet_k100_log.txt"
topics = pd.read_csv(log_topics, sep = ":", header = None, skiprows=2)
topics.columns = topics.columns = ["topic", "words"]
d = pd.read_csv("/work/50114/twitter/data/nlp/msg_network/os_rc_5_typeretweet_k100_prune2.0.csv")

# modify topics
topics["topic"] = [int(re.sub("dimension-", " ", x)) for x in topics["topic"]]

## label all the topics ##
dct_topic = {}
dct_coherence = {}
dct_interest = {}
for i in range(len(topics)):
    print(topics[topics["topic"] == i])
    topic_label = input("topic label: ")
    topic_coherency = input("topic coherency: ")
    topic_interest = input("topic interest: ")
    dct_topic[i] = topic_label
    dct_coherence[i] = topic_coherency
    dct_interest[i] = topic_interest

d_label = pd.DataFrame(
    dct_topic.items(),
    columns = ["topic", "label"])

d_coherence = pd.DataFrame(
    dct_coherence.items(),
    columns = ["topic", "coherence"]
)

d_interest = pd.DataFrame(
    dct_interest.items(),
    columns = ["topic", "topic_interest"]
)

d2 = d_label.merge(d_coherence, on = "topic", how = "inner")
d3 = d2.merge(d_interest, on = "topic", how = "inner")

# topics back in
d4 = d3.merge(topics, on = "topic", how = "inner")

# save labels
## additional remove (11)
d4.to_csv("/work/50114/twitter/data/nlp/msg_network/os_rc_5_typeretweet_k100_topics.csv", index = False)
