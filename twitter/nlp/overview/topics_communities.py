'''
VMP 2022-05-06: 
overview of topics & communities.
from the main semantic analysis. 
'''

import pandas as pd 
pd.set_option('display.max_colwidth', None)
import numpy as np

# import files 
community = pd.read_csv("/work/50114/twitter/data/nlp/msg/network_topics/os_rc_5_typeretweet_k100_community_df0.8.csv")
topics = pd.read_csv("/work/50114/twitter/data/nlp/msg/network_tweets/os_rc_5_typeretweet_k100_topics.csv")

# data curation
## first ten words of each topic
topics["words"] = [",".join(x.split(",")[0:10]) for x in topics["words"]]

## label communities
community_labels = pd.DataFrame({
    'community': [0, 1, 2, 3, 4],
    'interpretation': ['Publication', 'Culture & Training', 'Data & Policy', 'Reform Psychology', 'OSF']}
)

community = community.merge(community_labels, on = "community", how = "inner")

## join with community
topics = topics.convert_dtypes()
community = community.convert_dtypes()

topic_comm = community.merge(topics, on = "topic", how = "outer")
#topic_comm["community"] = topic_comm["community"].replace(np.nan, "None")
topic_comm = topic_comm.sort_values('topic')

##### check by community (the topics that make sense) #####
topic_osf = topic_comm[topic_comm["interpretation"] == "OSF"]
topic_osf.head(10) # OSF good

topic_culture = topic_comm[topic_comm["interpretation"] == "Culture & Training"]
topic_culture.head(20) # culture good 

topic_data = topic_comm[topic_comm["interpretation"] == "Data & Policy"]
topic_data.head(10) # data is good 

topic_rep = topic_comm[topic_comm["interpretation"] == "Reform Psychology"]
topic_rep.head(20) # reform is good

topic_pub = topic_comm[topic_comm["interpretation"] == "Publication"]
topic_pub.head(20) # publication good 

#### check the stuff that does not make sense ####
topic_na = topic_comm[topic_comm["community"].isna()]

## low coherence 
topic_low_coherence = topic_na[topic_na["coherence"] == "low"]
topic_low_coherence.head(40)

## low interest
topic_low_interest = topic_na[topic_na["topic_interest"] == "low"]
topic_low_interest.head(40)

#### write overall table ####
topic_table = topic_comm[["topic", "interpretation", "words"]]
topic_table.to_csv("/work/50114/twitter/data/nlp/SI/topic_comm.csv", index = False)

topic_table = topic_table.rename(columns = {
    'topic': 'Topic',
    'interpretation': 'Community',
    'words': '10 most weighted words'
})

def write_latex(d, outname): 
    '''
    d: <pd.dataframe> 
    outname: <str> 
    '''

    d_latex = d.to_latex(
        multicolumn=True, 
        header=True, 
        index_names=False,
        index=False, 
        column_format='p{1cm}|p{3cm}|p{8cm}'
        )

    with open(f"{outname}.txt", 'w') as f: 
        f.write(d_latex)

out = "/work/50114/twitter/data/nlp/SI/topic_comm_table.txt"
write_latex(topic_table, out)