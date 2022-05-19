'''
VMP 2022-04-19: 
Plot total volume over time for various search-terms.
NB: re-use plot code from networks. 
'''

# imports 
import pandas as pd 
import numpy as np 
import pickle 
import seaborn as sns 
import matplotlib.pyplot as plt 
import datetime, time
from matplotlib.lines import Line2D
from itertools import product

## plot setup: https://colorbrewer2.org/#type=sequential&scheme=YlOrRd&n=3
#col_openscience = {'dark': "#3182bd", 'light': "#9ecae1"}
#col_replication = {'dark': '#e6550d', 'light': '#fdae6b'}
#col_reproducibility = {'dark': '#31a354', 'light': '#a1d99b'}
#col_keyword = {'dark': '#756bb1', 'light': '#bcbddc'}
col_dct = {'openscience': "#3182bd", 'replication': '#e6550d', 'reproducibility': '#31a354', 'keyword': '#756bb1'}
text_dct = {'title': 18, 'label': 14, 'major_tick': 12, 'minor_tick': 10}

### paths 
outpath = "/work/50114/twitter/fig/EDA"
repcrisis = "/work/50114/twitter/data/raw/preprocessed/replicationcrisis.pickle"
opensci = "/work/50114/twitter/data/raw/preprocessed/openscience.pickle"
overlap = "/work/50114/twitter/data/nlp/subsets/os_rc_overlap_concat.pickle"

### read 
def read_pickle(filename): 
    with open(f"{filename}", "rb") as f: 
        dct = pickle.load(f)
    d = pd.DataFrame.from_dict(dct)
    return d

d_repcrisis = read_pickle(repcrisis)
d_opensci = read_pickle(opensci)

### clean
def subset_cols(df): 
    subset_cols = ["main_author_username", "ref_author_username", "main_text", "type_tweet", "main_tweet_date"]
    df = df[subset_cols]
    df = df.rename(columns = {
        'main_author_username': 'username_from',
        'ref_author_username': 'username_to'
    })
    return df

d_repcrisis = subset_cols(d_repcrisis)
d_opensci = subset_cols(d_opensci)

d_repcrisis["category"] = "replicationcrisis"
d_opensci["category"] = "openscience"
d_concat = pd.concat([d_repcrisis, d_opensci])

d_concat["main_tweet_date"].min() # 2007
d_concat["main_tweet_date"].max() # 2021

### log some information ###
## number of tweets 
len(d_repcrisis) # 76.515
len(d_opensci) # 2.003.614
len(d_concat) # 2.080.129 (76.515 + 2.003.614)

## number of tweets that are not retweets
len(d_repcrisis[d_repcrisis["type_tweet"] != "retweeted"]) # 34.756
len(d_opensci[d_opensci["type_tweet"] != "retweeted"]) # 618.134 

### number of unique accounts ###
def edgelist_to_authors(d, from_col, to_col):
    df_src_authors = d[[from_col]]
    df_trg_authors = d[[to_col]].rename(columns = {to_col: from_col})
    df_concat_authors = pd.concat([df_src_authors, df_trg_authors])
    df_authors_edgelist = df_concat_authors.drop_duplicates()
    df_authors_edgelist = df_authors_edgelist.rename(columns = {from_col: 'username'})
    print(len(df_authors_edgelist)) 
    return df_authors_edgelist

d_repcrisis_edgelist = edgelist_to_authors(d_repcrisis, "username_from", "username_to") # 44.597
d_opensci_edgelist = edgelist_to_authors(d_opensci, "username_from", "username_to") # 367.261
d_concat_edgelist = edgelist_to_authors(d_concat, "username_from", "username_to") # 393.618

### authors that appear in both data-sets ###
d_intersection_edgelist = d_repcrisis_edgelist.merge(d_opensci_edgelist, on = "username", how = "inner")
d_intersection_edgelist = d_intersection_edgelist.rename(columns = {'username': 'username_from'})
len(d_intersection_edgelist) # 18.240 accounts appear in both data-sets 
d_intersection = d_concat.merge(d_intersection_edgelist, on = "username_from", how = "inner")
len(d_intersection) # 699.885 (including retweets)
len(d_intersection[d_intersection["type_tweet"] != "retweeted"]) # 177.654 (original)

### only authors from repcrisis that are only in repcrisis (same for openscience) ##
d_repcrisis_tmp = d_repcrisis.merge(d_intersection, on = ["username_from", "username_to", "main_text", "type_tweet", "main_tweet_date"], how = "outer")
d_repcrisis_only = d_repcrisis_tmp[(d_repcrisis_tmp["category_x"] == "replicationcrisis") & (d_repcrisis_tmp["category_y"].isnull())]
len(d_repcrisis_only) # 31.503 (out of 76.515)
d_repcrisis_only = d_repcrisis_only.drop(columns = {'category_y'})
d_repcrisis_only = d_repcrisis_only.rename(columns = {'category_x': 'category'})

d_opensci_tmp = d_opensci.merge(d_intersection, on = ["username_from", "username_to", "main_text", "type_tweet", "main_tweet_date"], how = "outer")
d_opensci_only = d_opensci_tmp[(d_opensci_tmp["category_x"] == "openscience") & (d_opensci_tmp["category_y"].isnull())]
len(d_opensci_only) # 1.348.741 
d_opensci_only = d_opensci_only.drop(columns = {'category_y'})
d_opensci_only = d_opensci_only.rename(columns = {'category_x': 'category'})

len(d_intersection) # 699.885 
total_records = 31503 + 1348741 + 699885 # (checks out)

## merge intersection into the data ##
d_intersection["category"] = "overlap"
d_total = pd.concat([d_repcrisis_only, d_opensci_only, d_intersection])
d_total.groupby('category').size() # 31.503/76.515 in repcrisis (more than 50% in overlap by volume)

# fix dates (date-time)
d_total["Date"] = pd.to_datetime(d_total["main_tweet_date"]).dt.date

d_total["Date"].min() # 2007
d_total["Date"].max() # 2021


# prepare plot 
## group years 
def group_time(df):
    '''
    df: <pd.dataframe> 
    '''

    # get counts
    df["Year"] = pd.DatetimeIndex(df['Date']).year # integer rather than period
    df = df.groupby(['Year', 'category']).size().reset_index(name = 'count').sort_values('Year', ascending = True)

    # full grid 
    all_years = [i for i in range(2007, 2022)] # 2022 to include 2021. 
    all_types = ["replicationcrisis", "openscience", "overlap"]

    df_combinations = pd.DataFrame(list(product(all_years, all_types)), columns=['Year', 'category'])

    # convert dtypes to avoid int --> float
    df_combinations = df_combinations.convert_dtypes()
    df = df.convert_dtypes()

    # merge back together 
    df_new = df_combinations.merge(df, on = ['Year', 'category'], how = 'left')
    df_new["count"] = df_new["count"].fillna(0)

    return df_new

# get it out 
d_year_all = group_time(d_total)
d_year_orig = group_time(d_total[d_total["type_tweet"] != "retweeted"])

############ ACTUALLY MAKE PLOT ##############
## Amount of data over time (incl. retweets)
# NB: need to color in the same way: 
#### --> overlap: tab:orange 
#### --> replicationcrisis: tab:purple 
#### --> openscience: tab:green

color_dct = {
    'openscience': 'tab:green',
    'replicationcrisis': 'tab:purple',
    'overlap': 'tab:orange'
}

lines = [
    Line2D([0], [0], color = color_dct.get("openscience")),
    Line2D([0], [0], color = color_dct.get("replicationcrisis")),
    Line2D([0], [0], color = color_dct.get("overlap"))]

labels = ['openscience', 'replicationcrisis', 'overlap']

fig, ax = plt.subplots(figsize = (8, 3), dpi = 300)
for i in d_year_all["category"].unique():
    d_tmp = d_year_all[d_year_all["category"] == i]
    d_tmp = d_tmp.sort_values('Year', ascending=True)
    y = list(d_tmp["count"])
    x = list(d_tmp["Year"])
    clrs = color_dct.get(i)
    ax.plot(x, y, color = clrs)
    #ax[i].tick_params(axis = 'both', which = 'major', labelsize = text_dct.get('major_tick'))
ax.set_xlabel('Year', size = text_dct.get('label'))
ax.set_ylabel('Tweets', size = text_dct.get('label'))
ax.legend(
    lines, 
    labels, 
    prop = {'size': text_dct.get('major_tick')}, 
    frameon=False,
    loc = "lower center", 
    bbox_to_anchor = (0.5, -0.4),
    ncol = 3)


## save 
outpath = "/work/50114/twitter/fig/EDA"
plt.savefig(f"{outpath}/volume_over_time_new.pdf", bbox_inches='tight')

## how much do they overlap?  --- we do not need a plot here, just numbers (unique authors) ##
# i.e. what percentage of tweeters in openscience are also in replicationcrisis?
total_overlap = len(d_intersection_edgelist) # 18.240 in both
total_opensci = len(d_opensci_edgelist) # 367.261 
total_repcrisis = len(d_repcrisis_edgelist) # 44.597
percent_opensci = total_overlap/total_opensci # 0.04966 (4.97%)
percent_repcrisis = total_overlap/total_repcrisis # 0.40899 (41%)

## only accounts that post original stuff ##
d_repcrisis_edgelist_orig = edgelist_to_authors(d_repcrisis[d_repcrisis["type_tweet"] != "retweeted"], "username_from", "username_to") # 44.597
d_opensci_edgelist_orig = edgelist_to_authors(d_opensci[d_opensci["type_tweet"] != "retweeted"], "username_from", "username_to")
d_overlap_edgelist_orig = d_repcrisis_edgelist_orig.merge(d_opensci_edgelist_orig, on = "username", how = "inner")
total_overlap = len(d_overlap_edgelist_orig) # 6.755
total_repcrisis = len(d_repcrisis_edgelist_orig) # 22.467
total_opensci = len(d_opensci_edgelist_orig) # 131.727
percent_opensci_orig = total_overlap/total_opensci # 0.05128 (5.13%)
percent_repcrisis_orig = total_overlap/total_repcrisis # 0.30066 (30.06%)

## not based on accounts, but based on volume ##
# actually do this (probably)


##### ACTUAL NICE CODE BELOW --- and old... #####

''' 1. subfield count '''
def plot_before_after_subplts(
    dfs, 
    x, 
    y,
    year, 
    clrs, 
    subfields, 
    figsize, 
    text_dct,
    outpath, 
    filename,
    type = 'bar'):

    '''
    dfs: <list> list of <pd.dataframe>
    x: <str> x variable
    y: <str> y variable
    year: <int> year to split by
    clrs: <list> list of <dict> 
    subfields: <list> list of subfields 
    figsize: <tuple>
    text_dct: <dict> text size 
    outpath: <str> overall outpath
    filename: <str> name of plot
    type = <str> defaults to 'bar', but can be 'fill'
    ''' 

    fig, ax = plt.subplots(
        1,
        4, 
        dpi = 300, 
        figsize = figsize, 
        sharex = True, 
        sharey = True) 

    for i, var in enumerate(zip(dfs, clrs, subfields)): 
        df = var[0]
        clr = var[1]
        sub = var[2]

        df_before = df[df[x] < year]
        df_after = df[df[x] >= year]

        x_before = list(df_before[x].values)
        y_before = list(df_before[y].values)
        x_after = list(df_after[x].values)
        y_after = list(df_after[y].values)

        if type == 'fill':
            ax[i].fill_between(x_before, y_before, 0, color = clr.get('dark'))
            ax[i].fill_between(x_after, y_after, 0, color = clr.get('light'))
        else: 
            ax[i].bar(x_before, y_before, color = clr.get('dark'))
            ax[i].bar(x_after, y_after, color = clr.get('light'))
        
        ax[i].set_title(sub, size = text_dct.get('title'))
        ax[i].tick_params(axis = 'both', which = 'major', labelsize = text_dct.get('major_tick'))
        ax[i].set_xlabel('Year', size = text_dct.get('label'))
        if i == 0: 
            ax[i].set_ylabel('Publications', size = text_dct.get('label'))
    
    fig.tight_layout()
    plt.savefig(f"{outpath}/{filename}.pdf")

## plot set-up
df_lst = [df_replication_year, df_keyword_year, df_openscience_year, df_reproducibility_year]
clrs_lst = [col_replication, col_keyword, col_openscience, col_reproducibility]
subfields_lst = ["$R_{FOS}$", "$R_{QUERY}$", "$OS_{FOS}$", "$R*_{FOS}$"]  
plot_name = 'subfield_count'

## plot it 
plot_before_after_subplts(
    dfs = df_lst, 
    x = 'Year',
    y = 'count',
    year = 2016,
    clrs = clrs_lst,
    subfields = subfields_lst,
    figsize = (8, 2.5),
    text_dct = text_dct,
    outpath = outpath,
    filename = plot_name)

''' 2. percent growth since 2005 '''
def plot_growth_after_year(
    dfs, 
    x, 
    y, 
    clrs, 
    sub_keys, 
    subfields,
    figsize, 
    text_dct,
    outpath, 
    filename,
    base_year = 2005):

    '''
    dfs: <list> list of <pd.dataframe>
    x: <str> x variable
    y: <str> y variable
    clrs: <list> list of <dict> 
    sub_keys: <list> list of subfield names that match keys in clrs
    subfields: <list> list of subfields 
    figtitle: <str> title for plot
    figsize: <tuple>
    text_dct: <dict> text size 
    outpath: <str> overall outpath
    filename: <str> name of plot
    base_year: <int> base-year
    ''' 

    # setup
    fig, ax = plt.subplots(
        dpi = 300, 
        figsize = figsize) 

    for i, var in enumerate(zip(dfs, sub_keys)): 
        # unpack
        df = var[0]
        sub_key = var[1]

        # prepare 
        df_base_count = df[df[x] == base_year][y].tolist()[0]
        df = df.assign(increase = lambda x: x[y] - df_base_count)
        df = df.assign(percent = lambda x: x["increase"] / df_base_count * 100)
        x_var = list(df[x].values)
        y_var = list(df["percent"].values)

        # plot 
        ax.plot(x_var, y_var, color = clrs.get(sub_key))

        if i == 0: 
            ax.set_title("Percentage Change", size = text_dct.get('title'))
            ax.tick_params(axis = 'both', which = 'major', labelsize = text_dct.get('major_tick'))
            ax.set_xlabel('Year', size = text_dct.get('label'))
            ax.set_ylabel('Percent', size = text_dct.get('label'))
        
    ax.xaxis.set_ticks(np.arange(base_year, 2021, 5)) 

    lines = [
        Line2D([0], [0], color = clrs.get(sub_keys[0])),
        Line2D([0], [0], color = clrs.get(sub_keys[1])),
        Line2D([0], [0], color = clrs.get(sub_keys[2])),
        Line2D([0], [0], color = clrs.get(sub_keys[3]))]

    labels = subfields
    ax.legend(lines, labels, prop = {'size': text_dct.get('major_tick')}, frameon=False)

    fig.tight_layout()
    plt.savefig(f"{outpath}/{filename}.pdf")

# plot 
color_keys = ['replication', 'keyword', 'openscience', 'reproducibility']
plot_growth_after_year(
    dfs = df_lst, 
    x = 'Year', 
    y = 'count', 
    clrs = col_dct, 
    sub_keys = color_keys, 
    subfields = subfields_lst,
    figsize = (8/2, 2.5), # half width
    text_dct = text_dct,
    outpath = outpath, 
    filename = 'subfield_percentage_change',
    base_year = 2005)


''' 3. relative size within psychology '''
# function
def plot_relative_size(
    df_meta,
    dfs, 
    x, 
    y, 
    clrs, 
    sub_keys, 
    subfields,
    figsize, 
    text_dct,
    outpath, 
    filename):

    '''
    df_meta: <pd.dataframe> meta dataframe (e.g. "psychology")
    dfs: <list> list of <pd.dataframe>
    x: <str> x variable
    y: <str> y variable
    clrs: <list> list of <dict> 
    sub_keys: <list> list of subfield names that match keys in clrs
    subfields: <list> list of subfields 
    figtitle: <str> title for plot
    figsize: <tuple>
    text_dct: <dict> text size 
    outpath: <str> overall outpath
    filename: <str> name of plot
    ''' 

    # setup
    fig, ax = plt.subplots(
        dpi = 300, 
        figsize = figsize) 

    for i, var in enumerate(zip(dfs, sub_keys)): 
        # unpack
        df = var[0]
        sub_key = var[1]

        # prepare 
        df_merged = df.merge(df_meta, on = 'Year', how = 'inner')
        df_merged = df_merged.assign(percent = lambda x: x["count"]/x["count_all"]*100)

        x_var = list(df_merged[x].values)
        y_var = list(df_merged["percent"].values)

        # plot 
        ax.plot(x_var, y_var, color = clrs.get(sub_key))

        if i == 0: 
            ax.set_title("Relative Size", size = text_dct.get('title'))
            ax.tick_params(axis = 'both', which = 'major', labelsize = text_dct.get('major_tick'))
            ax.set_xlabel('Year', size = text_dct.get('label'))
            ax.set_ylabel('Percent', size = text_dct.get('label'))
        
    ax.xaxis.set_ticks(np.arange(2005, 2021, 5)) 

    #lines = [
    #    Line2D([0], [0], color = clrs.get(sub_keys[0])),
    #    Line2D([0], [0], color = clrs.get(sub_keys[1])),
    #    Line2D([0], [0], color = clrs.get(sub_keys[2])),
    #    Line2D([0], [0], color = clrs.get(sub_keys[3]))]

    #labels = subfields
    #ax.legend(lines, labels, prop = {'size': text_dct.get('major_tick')}, frameon=False)
    #ax.get_legend().remove()

    fig.tight_layout()
    plt.savefig(f"{outpath}/{filename}.pdf")

# prepare plot 
## aggregate year 
df_meta_year = group_time(df_meta_clean)
'''
## add identifier column
df_meta_year["field"] = 'Psychology'
df_openscience_year['subfield'] = 'Open Science'
df_replication_year['subfield'] = 'Replication'
df_reproducibility_year['subfield'] = 'Reproducibility'
'''
## rename column
df_meta_year = df_meta_year.rename(columns = {'count': 'count_all'})

## collect vars 
dfs = [df_openscience_year, df_replication_year, df_reproducibility_year]

## plot
plot_relative_size(
    df_meta = df_meta_year,
    dfs = df_lst, 
    x = 'Year', 
    y = 'count', 
    clrs = col_dct, 
    sub_keys = color_keys, 
    subfields = subfields_lst,
    figsize = (8/2, 2.5), # half width
    text_dct = text_dct,
    outpath = outpath, 
    filename = 'subfield_percentage_overall')

