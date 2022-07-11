'''
VMP 2022-04-22:
topics over time volume
'''

# imports
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from matplotlib.lines import Line2D
from itertools import product
pd.set_option('display.max_colwidth', None)

text_dct = {'title': 18, 'label': 14, 'major_tick': 12, 'minor_tick': 10}

# load data
d_community = pd.read_csv("/work/50114/twitter/data/nlp/msg/network_topics/os_rc_5_typeretweet_k100_community_df0.8.csv")
d_topics = pd.read_csv("/work/50114/twitter/data/nlp/msg/network_tweets/os_rc_5_typeretweet_k100_topics.csv")
d_main = pd.read_csv("/work/50114/twitter/data/nlp/msg/network_topics/os_rc_5_typeretweet_k100.csv")
d_authors = pd.read_csv("/work/50114/twitter/data/nlp/msg/semantic_tweets/os_rc_5_typeretweet_k100_prune2.0_nmf.csv")

# check data
d_community.head(5) # all communities (unlabelled)
d_topics.head(10) # all topics with labels, score and words -- can inner join with community if we need
d_main.head(5) # weight between source/target (communities)
d_authors.head(5) # all posts with W_max and W_val

# fix community
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

d_community = d_community.merge(d_label, on = "community", how = "inner")
d_community = d_community.merge(d_nodecolor, on = "community", how = "inner")

# merge communities on authors (also removes half of our topics)
d_community = d_community.rename(columns = {'topic': 'W_max'}) # W_max
d_authors = d_authors.merge(d_community, on = "W_max", how = "inner")

# fix time/date 
## create variable and group data
d_authors["Date"] = pd.to_datetime(d_authors["tweet_data"]).dt.date
d_authors["Year"] = pd.DatetimeIndex(d_authors['Date']).year

def group_var_year(d, var):
    '''
    d: <pd.dataframe>
    var: <str> column name of grouping var
    '''
    d_year = d.groupby([var, 'Year']).size().reset_index(name = 'count')
    return d_year

d_topic_year = group_var_year(d_authors, "W_max")
d_comm_year = group_var_year(d_authors, "community")

## create grid & fill (do with community first  then make general)
def fill_grid(d1, d2, var): 
    '''
    d1: <pd.dataframe> e.g. d_authors, main dataframe
    d2: <pd.dataframe> e.g. d_topic_year, specific dataframe
    var: <str> column name
    '''
    # create grid
    year_grid = [i for i in range(d1["Year"].min(), d1["Year"].max()+1)]
    var_grid = sorted(list(d1[var].unique())) 

    d_grid = pd.DataFrame(
        list(product(year_grid, var_grid)),
        columns = ["Year", var]
    )
    
    # fix dtypes
    d2 = d2.convert_dtypes()
    d_grid = d_grid.convert_dtypes()
    
    # merge
    d_merge = d_grid.merge(d2, on = ["Year", var], how = "left")
    d_merge["count"] = d_merge["count"].fillna(0)

    # return
    return d_merge

d_topic_grid = fill_grid(d_authors, d_topic_year, "W_max")
d_comm_grid = fill_grid(d_authors, d_comm_year, "community")

## plot most common topics ## 
## some issue with hue here... ##
dct_label = d_label.set_index("community").to_dict("index")
dct_color = d_nodecolor.set_index("community").to_dict("index")
dct_events = { # find references or other major events
    'Feeling the Future': 2011,
    'OSF': 2013,
    'OSC': 2015
}

## labels
lines = [
    Line2D([0], [0], color = dct_color[0]["color"]),
    Line2D([0], [0], color = dct_color[1]["color"]),
    Line2D([0], [0], color = dct_color[2]["color"]),
    Line2D([0], [0], color = dct_color[3]["color"]),
    Line2D([0], [0], color = dct_color[4]["color"])
    ]

labels = [val["label"] for key, val in dct_label.items()]

## label with lines indicating major events 
## e.g. OSC, BEM, OSF LAUNCH
def plot_community(figsize, d, dct_color, text_dct, lines, labels, outpath, filename): 

    # setup
    fig, ax = plt.subplots(dpi = 300, figsize = (8, 3))

    # plot lines
    for community in d_comm_grid["community"].unique():
        d_comm_sub = d_comm_grid[d_comm_grid["community"] == community]
        d_comm_sub_sorted = d_comm_sub.sort_values('Year', ascending=True)
        y1 = list(d_comm_sub_sorted["count"])
        x1 = list(d_comm_sub_sorted["Year"])
        ax.plot(x1, y1, alpha = 1, linewidth = 2, color = dct_color.get(community)["color"])

    # formatting
    ax.tick_params(axis = 'both', which = 'major', labelsize = text_dct.get('major_tick'))
    ax.set_xlabel('Year', size = text_dct.get('label'))
    ax.set_ylabel('Frequency', size = text_dct.get('label'))
    ax.legend(lines, labels, prop = {'size': text_dct.get('major_tick')}, frameon=False)

    # save 
    fig.tight_layout()
    plt.savefig(f"{outpath}/{filename}.pdf")

## generate plot
plot_community(
    figsize = (8, 3),
    d = d_comm_grid, 
    dct_color = dct_color, 
    text_dct = text_dct,
    lines = lines,
    labels = labels,
    outpath = "/work/50114/twitter/fig/nlp/msg/topics",
    filename = "os_rc_5_typeretweet_k100_community_over_time_new"
)

##### currently not included #####
## add vlines (BEM, OSC, OSF)
## also, loosing steam? (need to double-check with full data)
#ymax = d_comm_grid["count"].max()
#for key, val in dct_events.items(): 

#    ax.vlines(
#        x = val,
#        ymin = 0,
#        ymax = 800,
#        color = 'black',
#        linestyle = "dashed"
#    )
