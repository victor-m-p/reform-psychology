import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
import datetime, time
pd.options.mode.chained_assignment = None  # default='warn'

# read stuff 
psych_paa = pd.read_csv("/work/50114/MAG/data/psychology_paper_author.csv")
psych_meta = pd.read_csv("/work/50114/MAG/data/psychology_paper_meta.csv")
psych_ref = pd.read_csv("/work/50114/MAG/data/psychology_reference.csv")

# fix date format
psych_meta["Date"] = pd.to_datetime(psych_meta["Date"]).dt.date

# number of unique papers 
len(psych_paa['PaperId'].unique()) # ~4.880.189
len(psych_meta['PaperId'].unique()) # ~2.138.960


psych_paa.head(2)