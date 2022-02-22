'''
VMP 2022-02-21: 
Test matching (not used in the analysis, just for development). 
Working solution: loop + merge_asof() 
Not super elegant, but does the job. 
Only drawback is that it does not guarantee best matching. 
But it should be pretty good.
'''

import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 

# create fake test data
d1 = pd.DataFrame({
    'n_authors': [1, 1, 1, 2, 3, 4, 4], # sorted by key
    'Date': [100, 100, 102, 105, 109, 110, 200],
    'NormalizedName': ['p', 'p', 'p', 'p', 'p', 'p', 'p'],
    'condition_exp': ['e', 'e', 'e', 'e', 'e', 'e', 'e'],
    'id_exp': ['e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7']
    })

d2 = pd.DataFrame({
    'n_authors': [1, 1, 1, 2, 3, 4, 5], # sorted by key
    'Date': [100, 100, 103, 110, 114, 130, 300],
    'NormalizedName': ['p', 'p', 'p', 'p', 'p', 'p', 'p'],
    'condition_con': ['c', 'c', 'c', 'c', 'c', 'c', 'c'],
    'id_con': ['c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7']
    })

# merge_asof() without looping 
## does not quite work, e.g. we would like e1-c1 and e2-c2 (or opposite), but not c2 twice.
d_asof = pd.merge_asof(
    d1, # this is the date we get
    d2, 
    on = 'Date', # can be "asof" (close match) 
    by = ['n_authors', 'NormalizedName'], # has to be equivalent
    direction = 'nearest')
d_asof

# merge_asof() with looping. 

def get_matches(d_exp, d_control):
    '''
    d_exp: <pd.dataframe> experimental condition
    d_control: <pd.dataframe> control condition
    ''' 
    
    # setup 
    d_loop = pd.DataFrame(
        columns = [
            "n_authors", 
            "Date",
            "NormalizedName",
            "condition_exp",
            "id_exp",
            "condition_con",
            "id_con"]
            )

    # loop 
    for i in range(len(d_exp)):

        # get the row  
        d_tmp = d_exp.iloc[i:i+1]

        # merge asof 
        d_asof = pd.merge_asof(
            d_tmp, # this is the date we get
            d_control, 
            on = 'Date', # can be "asof" (close match) 
            by = ['n_authors', 'NormalizedName'], # has to be equivalent
            direction = 'nearest')

        # remove used index (control)
        used_index = d_asof["id_con"].item()    
        d_control = d_control[d_control["id_con"] != used_index]

        # append 
        d_loop = d_loop.append(d_asof)
    
    # return 
    return(d_loop)
        
d = get_matches(d1, d2)
d # pretty good, does not ensure best match, but pretty good. 
