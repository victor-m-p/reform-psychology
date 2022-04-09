'''
VMP 2022-03-12: 
plot citations over time: 
(1) all of them in a crazy plot (all starting at "publication")
(2) a function in which we can plot a specific one 

mainly ment as plots to make it clear to readers what we are modeling.

'''

# packages
import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import math
from matplotlib import cm
from matplotlib.colors import ListedColormap,LinearSegmentedColormap
from itertools import product
from matplotlib.lines import Line2D

# read it 
d = pd.read_csv("/work/50114/MAG/data/modeling/psychology_replication_EDA.csv")

len(d["PaperId"].unique()) # only those cited (n = 955 for both groups total)

# select columns (for now)
d = d[["condition", "PaperId", "time_gap_int"]]

# common preprocessing
one_year = 365 
max_date = 1825 # 5 * 365
d["year_diff"] = [math.ceil(x/one_year) for x in d["time_gap_int"]]

# for all of the plots below: 
d_grouped = d.groupby(['condition', 'PaperId', 'year_diff']).size().reset_index(name = 'count')
max_citation = d_grouped.groupby('PaperId')['count'].sum().reset_index(name = 'total_citations')['total_citations'].max()

# grid 
unique_yeardiff = [1, 2, 3, 4, 5]
unique_paperid = list(d_grouped['PaperId'].unique())
d_grid = pd.DataFrame(list(product(unique_paperid, unique_yeardiff)), columns=['PaperId', 'year_diff'])
d_condition = d_grouped[["PaperId", "condition"]].drop_duplicates()
d_grid = d_grid.merge(d_condition, on = "PaperId", how = 'inner')
d_grid = d_grid.convert_dtypes()
d_grouped = d_grouped.convert_dtypes()
d_cleaned = d_grid.merge(d_grouped, on = ['PaperId', 'year_diff', 'condition'], how = 'left')
d_cleaned["count"] = d_cleaned["count"].fillna(0)

# find a good example: 
d_replication = pd.read_csv("/work/50114/MAG/data/modeling/psychology_replication_matched.csv")
d_replication = d_replication[["match_group", "PaperId", "Year", "PaperTitle", "n_authors"]]

# join
d_metadata = d_replication.merge(d_cleaned, on = "PaperId", how = "inner")

# find top studies (replication)
d_top = d_metadata[
    (d_metadata["condition"] == "experiment") & 
    (d_metadata["year_diff"] == 5) &
    (d_metadata["count"] > 15)]

## try to find studies that make sense to show as example
def get_match(d, match_group):
    '''
    d: <pd.dataframe> 
    match_group: <int> 
    '''
    d = d[
        (d["condition"] == "experiment") &
        (d["match_group"] == match_group)
    ]

    return d

# just manylabs and schooler 
## two large-scale replication efforts 
d_manylabs = get_match(d_metadata, 443) # nuanced (starts: 20)
d_schooler = get_match(d_metadata, 508) # increasing (starts: 12) 
d_pospsych = get_match(d_metadata, 301) # nuanced 


## plot them together ## 
def plot_figure(d_main, d_study1, d_study2, figsize, color, text_dct, outpath, filename, cutoff = 300): 
    # setup 
    fig, ax = plt.subplots(1, 2, figsize = figsize, dpi = 300, sharey = True)

    ### subplot 1 ###
    x1 = ["$c_1$", "$c_2$", "$c_3$", "$c_4$", "$c_5$"]
    ## plot each line 
    for idx in d_main["PaperId"].unique():
        d_sub = d_main[d_main["PaperId"] == idx]
        d_sub = d_sub.sort_values('year_diff', ascending = True)
        d_sub["cumsum"] = d_sub["count"].cumsum()
        y1 = list(d_sub["cumsum"].values)
        if max(y1) <= cutoff: 
            ax[0].plot(x1, y1, alpha = 0.5, linewidth = 0.5, color = "#fdae6b")

    ## plot average line 
    n_papers = len(d_main['PaperId'].unique()) 
    n_citations = d_main.groupby('year_diff')['count'].sum().reset_index(name = 'count')
    n_citations["cumsum"] = n_citations["count"].cumsum()
    y1 = [x/n_papers for x in n_citations["cumsum"]]
    ax[0].plot(x1, y1, alpha = 1, linewidth = 1.5, color = "#e6550d")
    ax[0].set_ylabel("Citations", size = text_dct.get("label"))

    ### subplot 2 ###
    for d_study, col in zip([d_study1, d_study2], color):
        d_study = d_study.sort_values("year_diff", ascending = True)
        d_study["cumsum"] = d_study["count"].cumsum()
        y1 = list(d_study["cumsum"].values)
        ax[1].plot(x1, y1, color = col) 

    lines = [
        Line2D([0], [0], color = color[0]),  
        Line2D([0], [0], color = color[1])]  

    labels = [
        "Richard A. Klein et al. (2014)",
        "V. K. Alogna et al. (2014)"
    ]
    
    ax[1].legend(lines, labels, prop = {'size': text_dct.get('minor_tick') + 1}, frameon=False)
    plt.tick_params(axis = 'both', which = 'major', labelsize = text_dct.get('major_tick'))
    #plt.ylabel("Citations")
    fig.tight_layout()
    plt.savefig(f"{outpath}/{filename}.pdf")

# plot setup
color =["#e6550d", "#fdae6b"]
text_dct = {'title': 18, 'label': 14, 'major_tick': 12, 'minor_tick': 10}

## actually plot them ##
plot_figure(
    d_main = d_cleaned,
    d_study1 = d_manylabs,
    d_study2 = d_schooler, 
    figsize = (8, 3),
    color = color,
    text_dct = text_dct,
    outpath = '/work/50114/MAG/fig/EDA',
    filename = 'citation_discussion'
)

### NB example ### 
# Manylabs receives $20$ citations in the first year following 
# Publication ($c_1 = 20$) while schooler receives $c_1 = 12$ 
# This initial difference compounds, as shown in the plot, 
# and manylabs ends up with $c_5 = 273$ while schooler ends up
# with $c_5 = 109$. What started as less than double the amount
# of citations to manylabs in the first year has compounded to 
# almost three times more citations for manylabs after five years. 

# manylabs teamsize: 51
# schooler teamsize: 91
## --> both large teams 

### NB general ### 
# for instance, the MAG does not classify "OSC 2015" as replication
# while this is likely the most important large-scale replication 
# project in psychology ever (see 6K citations). 

# we will not manually add this study however, since we do not 
# want to bias the sample. We note that the overall data is reasonable
# and both the MAG (and specifically sub-categories "reproducibility" and
# "open science" has been used in prior research). 