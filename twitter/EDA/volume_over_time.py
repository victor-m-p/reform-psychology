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
col_openscience = {'dark': "#3182bd", 'light': "#9ecae1"}
col_replication = {'dark': '#e6550d', 'light': '#fdae6b'}
col_reproducibility = {'dark': '#31a354', 'light': '#a1d99b'}
col_keyword = {'dark': '#756bb1', 'light': '#bcbddc'}
col_dct = {'openscience': "#3182bd", 'replication': '#e6550d', 'reproducibility': '#31a354', 'keyword': '#756bb1'}
text_dct = {'title': 18, 'label': 14, 'major_tick': 12, 'minor_tick': 10}

# paths 
basepath = "/work/50114/twitter/data"
outpath = "/work/50114/twitter/fig/EDA"
repcrisis = f"{basepath}/raw/preprocessed/replicationcrisis.pickle"
opensci = f"{basepath}/raw/preprocessed/openscience.pickle"
intersection = f"{basepath}/nlp/subsets/openscience_replicationcrisis_intersection.pickle"

# read 
def read_pickle(filename): 
    with open(f"{filename}", "rb") as f: 
        dct = pickle.load(f)
    d = pd.DataFrame.from_dict(dct)
    return d

d_repcrisis = read_pickle(repcrisis)
d_opensci = read_pickle(opensci)
d_intersection = read_pickle(intersection)

# select useful columns 
def subset_cols(d, cols): 
    '''
    d: <pd.dataframe> 
    cols: <str> 
    '''
    d = d[cols]
    return d

## setup 
focus_cols = ["type_tweet", "main_author_username", "main_tweet_date", "ref_tweet_date"]

## subset
d_repcrisis = subset_cols(d_repcrisis, focus_cols)
d_opensci = subset_cols(d_opensci, focus_cols)
d_intersection = subset_cols(d_intersection, focus_cols)

# NB: fix dates -- should be ref_tweet_date, unless "None".  

# gather in one frame 
d_repcrisis["type"] = "rc"
d_opensci["type"] = "os"
d_intersection["type"] = 'rc_os'

d_total = pd.concat([d_repcrisis, d_opensci, d_intersection])

# fix dates (date-time)
d_total["Date"] = pd.to_datetime(d_total["main_tweet_date"]).dt.date

# group by period 
#d_total["Year"] = pd.DatetimeIndex(d_total["Date"]).year # we could also try with month
#d_year = d_total.groupby(['Year', 'type']).size().reset_index(name = 'count').sort_values('Year', ascending = True)

# prepare plot 
## group years 
def group_time(df):
    '''
    df: <pd.dataframe> 
    '''

    # get counts
    df["Year"] = pd.DatetimeIndex(df['Date']).year # integer rather than period
    df = df.groupby(['Year', 'type']).size().reset_index(name = 'count').sort_values('Year', ascending = True)

    # full grid 
    all_years = [i for i in range(2007, 2021)]
    all_types = ["rc", "os", "rc_os"]

    df_combinations = pd.DataFrame(list(product(all_years, all_types)), columns=['Year', 'type'])

    # convert dtypes to avoid int --> float
    df_combinations = df_combinations.convert_dtypes()
    df = df.convert_dtypes()

    # merge back together 
    df_new = df_combinations.merge(df, on = ['Year', 'type'], how = 'left')
    df_new["count"] = df_new["count"].fillna(0)

    return df_new

# get it out 
d_year = group_time(d_total)

## almost all those that interact with "replicationcrisis" interact with "openscience".
## this is not true the other way around.
## Of course, does not mean that everyone agrees with everything coming from "openscience", but at least they engage: 
## --> e.g. in this set is also the preregistration/openscience sceptics (e.g. Iris, Olivia, Berna, etc.)
sns.lineplot(
    data = d_year, 
    x = "Year", 
    y = "count", 
    hue = "type")

##### ACTUAL NICE CODE BELOW #####

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

