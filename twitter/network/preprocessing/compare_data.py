'''
VMP 2022-04-09: 
Check amount of data in different samples.
'''

# imports 
import pandas as pd
import numpy as np
import pickle 
pd.set_option('display.max_colwidth', None)

# read data
def read_pickle(query): 
    with open(f"/work/50114/twitter/data/raw/preprocessed/{query}.pickle", "rb") as f: 
        dct = pickle.load(f)
        
    d = pd.DataFrame.from_dict(dct)
    return d 

d_bropenscience = read_pickle("bropenscience")
d_repcrisis = read_pickle("replicationcrisis")
d_openscience = read_pickle("openscience")
d_replicability = read_pickle("replicability")
d_reproducibility = read_pickle("reproducibility")
d_openresearch = read_pickle("openresearch")

# check raw amount
len(d_bropenscience) #3.7K (very low)
len(d_repcrisis) # 76.5K (decent)
len(d_openscience) # 2M (much larger)
len(d_replicability) # 236 (nothing)
len(d_reproducibility) # 2.7K (very low)
len(d_openresearch) # 233K (check this - could be a bad sample)