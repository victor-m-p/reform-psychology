'''
VMP 2022-04-02: 
Representation in different groups over time: 
* Replication (FoS)
* Reproducibility (FoS)
* Open Science (FoS)
* Replication (Title)

Returns: 
* Plot of data (2005-2015, 2016-2020)
* Plot of fraction (2005-2020)
* Plot of % increase (2005-2020)
* .csv with key data to report 
'''

# imports 
import pandas as pd 
import seaborn as sns 
import matplotlib.pyplot as plt 
import datetime, time
import numpy as np
from matplotlib.lines import Line2D

# vars 
field = 'psychology'
keyword = 'replicat'
outpath = '/work/50114/MAG/fig/EDA'

## plot setup: https://colorbrewer2.org/#type=sequential&scheme=YlOrRd&n=3
col_openscience = {'dark': "#3182bd", 'light': "#9ecae1"}
col_replication = {'dark': '#e6550d', 'light': '#fdae6b'}
col_reproducibility = {'dark': '#31a354', 'light': '#a1d99b'}
col_keyword = {'dark': '#756bb1', 'light': '#bcbddc'}
col_dct = {'openscience': "#3182bd", 'replication': '#e6550d', 'reproducibility': '#31a354', 'keyword': '#756bb1'}
text_dct = {'title': 18, 'label': 14, 'major_tick': 12, 'minor_tick': 10}

# read data
df_meta = pd.read_csv(f"/work/50114/MAG/data/raw/{field}_paper_meta_clean.csv")
df_openscience = pd.read_csv(f"/work/50114/MAG/data/raw/{field}_openscience.csv")
df_replication = pd.read_csv(f"/work/50114/MAG/data/raw/{field}_replication.csv")
df_reproducibility = pd.read_csv(f"/work/50114/MAG/data/raw/{field}_reproducibility.csv")

# preprocessing: 
## get candidate papers 
def clean_meta(df_meta, fos): 
    '''
    df_meta: <pd.dataframe> dataframe (meta) to be cleaned
    fos: <str> main field of study (e.g. "psychology")
    '''

    # date cannot be na 
    df_meta = df_meta[~df_meta["Date"].isna()]
    df_meta["Date"] = pd.to_datetime(df_meta["Date"]).dt.date
    df_meta = df_meta.rename(columns = {'NormalizedName': 'NormalizedNameMain'})

    # need to account for this one 
    if fos == "politicalscience":
        fos = "political science"

    df_clean = df_meta[
    (df_meta["NormalizedNameMain"] == fos) &
    ((df_meta["DocType"] == 'Journal') | (df_meta["DocType"] == 'Conference')) & 
    (df_meta["Date"] >= datetime.date(2005, 1, 1)) & 
    (df_meta["Date"] < datetime.date(2021, 1, 1))
    ]

    return df_clean

## run function 
df_meta_clean = clean_meta(df_meta, 'psychology')

## get the subset for fos (inner join)
def get_subfield(df_meta_clean, df_subfield):
    '''
    df_meta_clean: <pd.dataframe> cleaned with 'clean_meta' function
    df_subfield: <pd.dataframe> subfield dataframe 
    '''
    # rename subfield column
    df_subfield = df_subfield.rename(columns = {'NormalizedName': 'NormalizedNameSub'})
    
    # merge 
    df_gathered = df_subfield.merge(df_meta_clean, on = 'PaperId', how = 'inner')

    return df_gathered

## get values out
### check that the number is right in (2005, 2015)
df_openscience_meta = get_subfield(df_meta_clean, df_openscience)
df_replication_meta = get_subfield(df_meta_clean, df_replication)
df_reproducibility_meta = get_subfield(df_meta_clean, df_reproducibility)

## get query subset 
df_keyword_meta = df_meta_clean.loc[df_meta_clean['PaperTitle'].str.contains(keyword, case=False)]

# check data
## length of original 
len(df_meta) # 6.770.202
len(df_openscience_meta) # 229
len(df_replication_meta) # 1434
len(df_reproducibility_meta) # 383
len(df_keyword_meta) # 2442

## check length in (2005, 2015) -- sanity check
def check_sublength(d):
    '''
    d: <pd.dataframe> 
    '''
    # records in (2005, 2015)
    d = d[
        (d["Date"] >= datetime.date(2005, 1, 1)) & 
        (d["Date"] < datetime.date(2016, 1, 1))]

    # print information
    print(f"{len(d)}")

check_sublength(df_openscience_meta) # 27 (correct)
check_sublength(df_replication_meta) # 620 (correct)
check_sublength(df_reproducibility_meta) # 228 (correct)
check_sublength(df_keyword_meta) # 1196 (correct)

# prepare plot 
## group years 
def group_time(df):
    '''
    df: <pd.dataframe> 
    '''

    # get counts
    df["Year"] = pd.DatetimeIndex(df['Date']).year # integer rather than period
    df = df.groupby('Year').size().reset_index(name = 'count').sort_values('Year', ascending = True)

    # full grid 
    all_years = [i for i in range(2005, 2021)]
    df_years = pd.DataFrame({'Year': all_years})

    # convert dtypes to avoid int --> float
    df_years = df_years.convert_dtypes()
    df = df.convert_dtypes()

    # merge back together 
    df_new = df_years.merge(df, on = 'Year', how = 'left')
    df_new["count"] = df_new["count"].fillna(0)

    return df_new

df_openscience_year = group_time(df_openscience_meta)
df_replication_year = group_time(df_replication_meta)
df_reproducibility_year = group_time(df_reproducibility_meta)
df_keyword_year = group_time(df_keyword_meta)

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

