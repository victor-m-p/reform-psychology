'''
VMP 2022-05-09: 
prosocial communities
'''

# loads
import pandas as pd 
import re 
import pickle
import matplotlib.pyplot as plt

# files 
## the words
df_words = pd.read_csv("/work/50114/twitter/nlp/basic_analysis/murphy_prosocial.csv")
d_authors = pd.read_csv("/work/50114/twitter/data/nlp/msg/semantic_tweets/os_rc_5_typeretweet_k100_prune2.0_nmf.csv")
d_community = pd.read_csv("/work/50114/twitter/data/nlp/msg/network_topics/os_rc_5_typeretweet_k100_community_df0.8.csv")

## only take the columns we need 
d_authors = d_authors[["tweet_id", "username", "W_max"]]
d_authors = d_authors.rename(columns = {'W_max': 'topic'})

## join with community (only the ones that are in a community)
d_comm = d_authors.merge(d_community, on = "topic", how = "inner")
d_comm.head(5)

## only the "core" set (intersection with two original posts) -- env. mark
infile_intersect = "/work/50114/twitter/data/nlp/subsets/os_rc_5.pickle"
with open(f"{infile_intersect}", "rb") as f:
    df_intersect = pickle.load(f)

# get the word list 
df_prosoc = df_words[df_words["IndivConstruct"] == "Prosocial Motives"]
df_prosoc = df_prosoc[["IndivConstruct", "Words"]]
lst_words = list(df_prosoc["Words"])

# only do .lower() -- not retweets
subset_cols = ["main_tweet_id", "type_tweet", "main_author_username", "main_text", "main_lang", "main_tweet_date"]
df_intersect = df_intersect[subset_cols] # only relevant columns 
df_intersect = df_intersect[df_intersect["main_lang"] == "en"]
df_intersect = df_intersect[df_intersect["type_tweet"] != "retweeted"] # no retweets
df_intersect["text_lower"] = [x.lower() for x in df_intersect["main_text"]]
df_intersect = df_intersect.rename(columns = {'main_tweet_id': 'tweet_id', 'main_author_username': 'username'})

## merge with communities
df_intersect["tweet_id"] = df_intersect["tweet_id"].astype(str).astype(int)
df_intersect = df_intersect.merge(d_comm, on = ["tweet_id", 'username'], how = "inner") # some small discrepancy


# find whether each tweet has prosocial construct  
df_intersect["prosoc"] = [any(ele in x for ele in lst_words) for x in df_intersect["text_lower"]]
df_counts = df_intersect.groupby(['community', 'prosoc']).size().reset_index(name = 'count')

# assign labels 
d_label = pd.DataFrame({
    "community": [0, 1, 2, 3, 4],
    "label": [
        "Publication", 
        "Culture & Training", 
        "Data & Policy",
        "Reform Psychology", 
        "OSF"]})

d_nodecolor = pd.DataFrame({
    "community": [0, 1, 2, 3, 4],
    "color": [
        "tab:blue",
        "tab:green",
        "tab:orange",
        "tab:red",
        "tab:purple"]})

df_counts = df_counts.merge(d_label, on = "community", how = "inner")
df_counts = df_counts.merge(d_nodecolor, on = "community", how = "inner")

# percents 
df_counts['percent'] = df_counts["count"] / df_counts.groupby('community')['count'].transform('sum')

## information
# Publication: 36.19%: 2727 out of 7535
# Culture & Training: 44.57%: 3112 out of 6983
# Data & Policy: 36.09%: 1717 out of 4757
# Reform Psych: 26.31%: 1941 out of 7377
# OSF: 28.21%: 693 out of 2457

# plot percent 
## prepare plot
df_counts_pos = df_counts[df_counts["prosoc"] == True]
df_counts_pos = df_counts_pos.sort_values('percent', ascending=False)
outfolder = "/work/50114/twitter/fig/EDA"
text_dct = {'title': 18, 'label': 14, 'major_tick': 12, 'minor_tick': 10}
## plot 
fig, ax = plt.subplots(figsize=(8,3), dpi = 300)
x_val = df_counts_pos["label"]
y_val = df_counts_pos["percent"]
c_val = df_counts_pos["color"]
plt.barh(x_val, y_val, color = c_val)
ax.invert_yaxis()
plt.suptitle('Prosocial Communities', size = text_dct.get('title'), x = 0.43)
ax.tick_params(axis = 'both', which = 'major', labelsize = text_dct.get('major_tick'))
ax.set_xlabel('Fraction Prosocial', size = text_dct.get('label'), x = 0.39)
plt.savefig(f"{outfolder}/prosocial_communities.pdf", bbox_inches='tight')

