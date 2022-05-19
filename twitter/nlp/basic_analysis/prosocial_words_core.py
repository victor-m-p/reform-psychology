'''
VMP 2022-05-09: 
replication of Murphy et al.
'''

# loads
import pandas as pd 
import re 
import pickle
import matplotlib.pyplot as plt

# files 
## the words
df_words = pd.read_csv("/work/50114/twitter/nlp/basic_analysis/murphy_prosocial.csv")

## only the "core" set (intersection with two original posts) -- env. mark
infile_intersect = "/work/50114/twitter/data/nlp/subsets/os_rc_5.pickle"
with open(f"{infile_intersect}", "rb") as f:
    df_intersect = pickle.load(f)

# get the word list 
df_prosoc = df_words[df_words["IndivConstruct"] == "Prosocial Motives"]
df_prosoc = df_prosoc[["IndivConstruct", "Words"]]
lst_words = list(df_prosoc["Words"])
len(lst_words)
## save this for SI ##
with open('/work/50114/twitter/nlp/basic_analysis/prosoc_terms.txt', 'w') as filehandle:
    for listitem in lst_words:
        filehandle.write('%s, ' % listitem)

# only do .lower() -- not retweets
subset_cols = ["type_tweet", "main_author_name", "main_text", "main_lang", "main_tweet_date"]
df_intersect = df_intersect[subset_cols] # only relevant columns 
df_intersect = df_intersect[df_intersect["main_lang"] == "en"]
df_intersect = df_intersect[df_intersect["type_tweet"] != "retweeted"] # no retweets
df_intersect["text_lower"] = [x.lower() for x in df_intersect["main_text"]]

# find whether each tweet has prosocial construct  
df_intersect["prosoc"] = [any(ele in x for ele in lst_words) for x in df_intersect["text_lower"]]

## amount / frequency
df_prosoc_size = df_intersect.groupby('prosoc').size().reset_index(name = 'count') 
df_prosoc_size = df_prosoc_size.assign(percent = lambda x: round(x["count"]/x["count"].sum(), 2))
df_prosoc_size.head(5)

# over time (year)
df_intersect["Date"] = pd.to_datetime(df_intersect["main_tweet_date"]).dt.date
df_intersect["Year"] = pd.DatetimeIndex(df_intersect['Date']).year # integer rather than period
df_intersect_year = df_intersect.groupby(['Year', 'prosoc']).size().reset_index(name = 'count').sort_values('Year', ascending = True)

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
ax1.set_ylabel('Proportion prosocial', size = text_dct.get('label'))
ax2.set_ylabel('Volume prosocial', size = text_dct.get('label'))
plt.suptitle('Prosocial terms', size = text_dct.get('title'))
plt.legend([l1, l2], ["Proportion prosocial", "Volume prosocial"])
outpath = "/work/50114/twitter/fig/EDA"
plt.savefig(f"{outpath}/prosocial_core.pdf", bbox_inches='tight')
