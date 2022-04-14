'''
try the Michele thing
'''

# imports 
import backboning 
import networkx as nx 
import pandas as pd 
import time
import numpy as np

''' functions '''
def label_users(d, query, ext):
    '''
    d: <pd.dataframe> 
    query: <str> 
    ext: <str>
    '''

    d = list(pd.unique(d[["username_from", "username_to"]].values.ravel('K'))) 
    d = pd.DataFrame({
        'user': d,
        f'query_{ext}': query
    })
    return d

def gather_queries(dfs, queries): 
    ''' 
    dfs: <list> list of two <pd.dataframe>
    queries: <list> list of two <str> 

    '''
    
    # unpack 
    d1, d2 = dfs 
    query1, query2 = queries

    # bind two frames
    df = pd.concat([d1, d2])
    df = df.groupby(['username_from', 'username_to'])['weight'].sum().reset_index(name = 'weight')

    # get unique users and their labels 
    d1_authors = label_users(d1, f"{query1}", "x")
    d2_authors = label_users(d2, f"{query2}", "y")

    d_clean = pd.merge(d1_authors, d2_authors, on = "user", how = "outer")

    ## bring it together
    conditions = [
        (d_clean['query_x'] == f'{query1}') & (d_clean['query_y'].isnull()),
        (d_clean['query_x'].isnull()) & (d_clean['query_y'] == f'{query2}')]
    choices = [f'{query1}', f'{query2}']

    d_clean['query'] = np.select(conditions, choices, default = 'Overlap')
    d_clean = d_clean.drop(columns = {'query_x', 'query_y'})

    return df, d_clean

# queries
query1 = "bropenscience"
query2 = "replicationcrisis"
inpath = "/work/50114/twitter/data/network/preprocessed"

# read data 
df1 = pd.read_csv(f"{inpath}/{query1}_edgelist_simple.csv")
df2 = pd.read_csv(f"{inpath}/{query2}_edgelist_simple.csv")

# prepare lists 
df_list = [df1, df2]
query_list = [query1, query2]

# gather queries
df, d_clean = gather_queries(df_list, query_list)

## relabel 
df_renamed = df.rename(columns = {
    'username_from': 'src',
    'username_to': 'trg',
    'weight': 'nij'
})



# their backboning stuff
## backboning noice corrected (NC)
## look up whether this works well for directed...
t1_nc = time.perf_counter()
table_nc = backboning.noise_corrected(df_renamed, undirected = True)
bb_neffke = backboning.thresholding(table_nc, 4)
t2_nc = time.perf_counter()
len(bb_neffke)
table_nc
table_df

## backboning disparity filter (DF)
t1_df = time.perf_counter()
table_df = backboning.disparity_filter(df_renamed, undirected = True)
bb_vespignani = backboning.thresholding(table_df, 0.66)
t2_df = time.perf_counter()

# check time 
print(f"NC took {t2_nc - t1_nc:0.4f} seconds")
print(f"DF took {t2_df - t1_df:0.4f} seconds")

## plot the backboning disparity filter (DF) GCC (to-do). 
