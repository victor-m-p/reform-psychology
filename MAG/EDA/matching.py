'''
VMP 2022-04-03: 
Check how good the matching is.
'''

# imports 
import pandas as pd 
import seaborn as sns 
import matplotlib.pyplot as plt 
import datetime, time
import numpy as np
from matplotlib.lines import Line2D

# Read data 
df_replication = pd.read_csv("/work/50114/MAG/data/modeling/psychology_replication_matched.csv")
df_replicat = pd.read_csv("/work/50114/MAG/data/modeling/psychology_replicat_matched.csv")

# total records
n_replication = len(df_replication)/2
n_replicat = len(df_replicat)/2

# function to give us number of perfectly matched records
def match_statistics(d, type):
    '''
    d: <pd.dataframe>
    type: <str> 
    '''

    # number of experiment records
    len_experiment = int(len(d)/2)

    # matched on year
    d = d.groupby(['match_group', 'Year']).size().reset_index(name = 'count')
    d = d.groupby(['match_group']).size().reset_index(name = 'N')
    d = d[d["N"] > 1]
    len_mismatch = len(d)
    len_match = int(len_experiment - len_mismatch)
    percent_mismatch = (len_match)/len_experiment
    
    # gather frame 
    d = pd.DataFrame({
        'type': [type], 
        'n_experiment': [len_experiment],
        'n_mismatch': [len_mismatch],
        'n_matched': [len_match],
        'perc_match': [percent_mismatch]})

    # return 
    return d 

# run the function
match_replication = match_statistics(df_replication, "replication_fos")
match_replicat = match_statistics(df_replicat, "replication_query")

# inspect
match_replication
match_replicat

# concat
d_match_statistics = pd.concat([match_replication, match_replicat])

# save
d_match_statistics.to_csv("/work/50114/MAG/data/EDA/match_statistics.csv", index = False)

