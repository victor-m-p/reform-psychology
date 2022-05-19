'''
VMP 2022-05-09: 
replication of Murphy et al.
'''

# loads
import pandas as pd 
import re 
import pickle
import matplotlib.pyplot as plt

## the words
df_words = pd.read_csv("/work/50114/twitter/nlp/basic_analysis/murphy_prosocial.csv")

## original files 
infile_openscience = "/work/50114/twitter/data/raw/preprocessed/openscience.pickle"
infile_repcrisis = "/work/50114/twitter/data/raw/preprocessed/replicationcrisis.pickle"

## read data & get filename
def read_data(infile):
    with open(f"{infile}", "rb") as f:
        dct = pickle.load(f)
    df = pd.DataFrame.from_dict(dct)
    return df 

df_open = read_data(infile_openscience)
df_rep = read_data(infile_repcrisis)

subset_cols = ["type_tweet", "main_author_username", "main_text", "main_lang", "main_tweet_date"]
df_open_sub = df_open[subset_cols]
df_rep_sub = df_rep[subset_cols]
df_open_sub["type"] = "openscience"
df_rep_sub["type"] = "replicationcrisis"

df_both = pd.concat([df_open_sub, df_rep_sub])

#### actual pipeline ####

# get the word list 
df_prosoc = df_words[df_words["IndivConstruct"] == "Prosocial Motives"]
df_prosoc = df_prosoc[["IndivConstruct", "Words"]]
lst_words = list(df_prosoc["Words"])

# only do .lower() -- not retweets
df_both = df_both[df_both["main_lang"] == "en"]
df_both = df_both[df_both["type_tweet"] != "retweeted"] # no retweets
df_both["text_lower"] = [x.lower() for x in df_both["main_text"]]


# find whether each tweet has prosocial construct  
df_both["prosoc"] = [any(ele in x for ele in lst_words) for x in df_both["text_lower"]]

## amount / frequency 
### ungrouped
df_both_overall = df_both[["type_tweet", "main_text", "main_lang", "main_author_username", "text_lower", "prosoc"]].drop_duplicates()
len(df_both_overall)

df_prosoc_size = df_both_overall.groupby('prosoc').size().reset_index(name = 'count') # True: 195.790 vs. False: 332.250 
df_prosoc_size = df_prosoc_size.assign(percent = lambda x: round(x["count"]/x["count"].sum(), 2))
df_prosoc_size.head(5) # True: 0.37 vs. False 0.63 

df_prosoc_group = df_both.groupby(['prosoc', 'type']).size().reset_index(name = 'count') # False OS (319.325), True OS (191.731), False R (24.682), True R (8.115)
df_prosoc_R = df_prosoc_group[df_prosoc_group["type"] == "replicationcrisis"]
df_prosoc_OS = df_prosoc_group[df_prosoc_group["type"] == "openscience"]
df_prosoc_R = df_prosoc_R.assign(percent = lambda x: round(x["count"]/x["count"].sum(), 2))
df_prosoc_OS = df_prosoc_OS.assign(percent = lambda x: round(x["count"]/x["count"].sum(), 2))
df_prosoc_R.head(5) # False: 0.75, True: 0.25
df_prosoc_OS.head(5) # False: 0.62, True: 0.38 

# over time (year)
df_both["Date"] = pd.to_datetime(df_both["main_tweet_date"]).dt.date
df_both["Year"] = pd.DatetimeIndex(df_both['Date']).year # integer rather than period
df_both_year = df_both.groupby(['Year', 'prosoc']).size().reset_index(name = 'count').sort_values('Year', ascending = True)

# plot (setup)
color_dct = {
    False: 'tab:red',
    True: 'tab:green'
}

## plot (percent & raw count)
text_dct = {'title': 18, 'label': 14, 'major_tick': 12, 'minor_tick': 10}
df_intersect_year.groupby(['Year', 'prosoc'])
df_intersect_total = df_intersect_year.groupby(['Year'])['count'].sum().reset_index(name = 'total_tweets')
df_frequency = df_intersect_total.merge(df_intersect_year, on = ['Year'], how = "inner")
df_frequency = df_frequency.assign(frequency = lambda x: x["count"]/x["total_tweets"])
df_true_frequency = df_frequency[df_frequency["prosoc"] == True]

fig, ax = plt.subplots(figsize = (8, 3), dpi = 300)
ax1 = plt.subplot()
x = list(df_true_frequency["Year"])
y1 = list(df_true_frequency["frequency"])
y2 = list(df_true_frequency["count"])
l1, = ax1.plot(x, y1, color = "tab:orange")
ax1.scatter(x, y1, color='tab:orange')
ax2 = ax1.twinx()
l2, = ax2.plot(x, y2, color = "tab:blue")
ax2.scatter(x, y2, color = "tab:blue")
ax.set_xlabel('Year', size = text_dct.get('label'))
ax1.set_ylabel('Proportion pro-social', size = text_dct.get('label'))
ax2.set_ylabel('Volume pro-social', size = text_dct.get('label'))
plt.suptitle('Pro-social terms', size = text_dct.get('title'))
plt.legend([l1, l2], ["Proportion pro-social", "Volume pro-social"])
outpath = "/work/50114/twitter/fig/EDA"
plt.savefig(f"{outpath}/prosocial_core.pdf", bbox_inches='tight')