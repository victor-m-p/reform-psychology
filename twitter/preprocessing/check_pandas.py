import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# open science
d = pd.read_csv("/work/50114/twitter/data/raw/preprocessed/openscience.csv")

len(d)
d.head(10) # conversation id fucked. 

# check dates
def check_dates(d): 
    d["tweet_created_at"] = d["tweet_created_at"].astype("datetime64[ns]") 
    d["tweet_created_at_year"] = d["tweet_created_at"].dt.year
    d_year = d.groupby('tweet_created_at_year').size().reset_index(name = "n_tweets")
    return d_year # did not get that far back...


# bropenscience (has declined somewhat)
# biggest fight in 2019 by far.
# already pretty interesting stuff.
d = pd.read_csv("/work/50114/twitter/data/raw/preprocessed/bropenscience.csv")

d_year = check_dates(d)
d_year