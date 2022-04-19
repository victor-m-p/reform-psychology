'''
VMP 2022-04-19: 
check the preprocessing
'''

# imports
import pandas as pd 
import numpy as np 

# paths 
path = "/work/50114/twitter/data/nlp/by_tweet/openscience_replicationcrisis_intersection_tweet_text.csv"

# import 
d = pd.read_csv(f"{path}")
