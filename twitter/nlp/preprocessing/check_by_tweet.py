'''
VMP 2022-04-19: 
check the preprocessing
'''

# imports
import pandas as pd 
import numpy as np 
import pickle

# read stuff
infile = "/work/50114/twitter/data/nlp/subsets/os_rc_5.pickle"
with open(f"{infile}", "rb") as f:
    dct = pickle.load(f)
df = pd.DataFrame.from_dict(dct)

# check it 
len(df) # 118932 rows 
len(df['main_author_name'].unique()) # 989 unique accounts -- this is what we should backbone

