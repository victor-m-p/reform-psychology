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

# read it 
d = pd.read_csv("/work/50114/MAG/data/modeling/psychology_replication_EDA.csv")

# select columns (for now)
d = d[["condition", "PaperId", "time_gap_int"]]

# common preprocessing
one_year = 365 
max_date = 1825 # 5 * 365
d["year_diff"] = [math.ceil(x/one_year) for x in d["time_gap_int"]]

# select one random study and plot it 
def plot_single_bar(d, id): 
    '''
    d: <pd.dataframe> 
    id: <str> 
    '''
    d_single = d[d["PaperId"] == id]
    year_N = d_single.groupby('year_diff').size().reset_index(name = 'count').sort_values('year_diff', ascending=True)
    x = list(year_N["year_diff"].values)
    y = list(year_N["count"].values)
    
    fig, ax = plt.subplots() 
    plt.bar(x, y) 
    plt.suptitle('Citations 5-year')
    ax.set_xlabel('Year after publication') #, size = text_dct.get('label'))
    ax.set_ylabel('Citations')
    plt.show(); 

plot_single_bar(d, 2270647624)

def plot_single_line(d, id): 
    '''
    d: <pd.dataframe> 
    id: <str> 
    '''
    d_single = d[d["PaperId"] == id]
    year_N = d_single.groupby('year_diff').size().reset_index(name = 'count').sort_values('year_diff', ascending=True)
    x = list(year_N["year_diff"].values)
    y = list(year_N["count"].values)
    
    fig, ax = plt.subplots() 
    plt.plot(x, y) 
    plt.suptitle('Citations 5-year')
    ax.set_xlabel('Year') #, size = text_dct.get('label'))
    ax.set_ylabel('Citations')
    plt.show(); 

plot_single_line(d, 2270647624)

''' plot all of the studies (by year) '''
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

## (1) color by group (control vs. experiment) 
### somehow replication in front here... 
# color, dark for replication studies, light for control
# https://www.color-hex.com/color-palette/1010074
def plot_grouped_condition(d): 

    col_tmp = {'experiment': "#990000", 'control': "#353354"}
    fig, ax = plt.subplots(figsize = (20, 10)) 
    for idx in d["PaperId"].unique():
        d1 = d[d["PaperId"] == idx]
        x1 = list(d1["year_diff"].values)
        y1 = list(d1["count"].values)
        condition = list(d1["condition"].values)[0]
        plt.plot(x1, y1, color = col_tmp.get(condition), alpha = 0.1)
    plt.show();

# works fine 
plot_grouped_condition(d_cleaned)

### cumulative ### 
# looks to linear? 
def plot_cumsum(d):
    col_tmp = {'experiment': "#990000", 'control': "#353354"}
    fig, ax = plt.subplots(figsize = (20, 10)) 
    for idx in d["PaperId"].unique():
        d1 = d[d["PaperId"] == idx]
        d1["cumsum"] = d1["count"].cumsum()
        x1 = list(d1["year_diff"].values)
        y1 = list(d1["cumsum"].values)
        condition = list(d1["condition"].values)[0]
        plt.plot(x1, y1, color = col_tmp.get(condition), alpha = 0.2)
    plt.show();
    return d1 

d1 = plot_cumsum(d_cleaned)

## (2) color by number of citations with ALPHA: 
col = "#990000"
fig, ax = plt.subplots(figsize = (20, 10))
for idx in d_grouped["PaperId"].unique(): 
    d1 = d_grouped[d_grouped["PaperId"] == idx]
    x1 = list(d1["year_diff"].values)
    y1 = list(d1["count"].values)
    alpha = sum(y1)/max_citation
    plt.plot(x1, y1, color = col, alpha = alpha)
plt.show(); 

