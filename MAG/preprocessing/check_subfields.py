'''
VMP 2022-03-11: 
testing whether the sub-categories make any sense

NB: 
actually should just get all openscience, reproducibility -
and replication along with their most dominant level 0 field. 
'''

# packages
import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
import datetime, time
from tqdm import tqdm
pd.options.mode.chained_assignment = None  # default='warn'
import os
import argparse 
from pathlib import Path

# setup 
pd.set_option('display.max_colwidth', None)
inpath = "/work/50114/MAG/data/raw"
field = "psychology"
subfield = "openscience"

# load data 
df_paa = pd.read_csv(f"{inpath}/{field}_paper_author.csv")
df_meta = pd.read_csv(f"{inpath}/{field}_paper_meta_clean.csv")
df_ref = pd.read_csv(f"{inpath}/{field}_reference.csv")
df_opensci = pd.read_csv(f"{inpath}/{field}_{subfield}.csv")

# openscience match on meta 
## we do not know how it is created, but after checking some (n = 4) it appears that 
## they are either tagged with "open science" and/or are "open access" and/or 
## available on OSF and/or mention "open science" in text. 
len(df_opensci)
open_merged = df_opensci.merge(df_meta, on = 'PaperId', how = 'inner')
open_merged.head(15)

# replication
df_replication = pd.read_csv(f"{inpath}/{field}_replication.csv")
len(df_replication)
rep_merged = df_replication.merge(df_meta, on = 'PaperId', how = 'inner')
rep_merged.head(5)

# reproducibility 
df_reproduce = pd.read_csv(f"{inpath}/{field}_reproducibility.csv")
len(df_reproduce)
reproduce_merged = df_reproduce.merge(df_meta, on = 'PaperId', how = 'inner')
reproduce_merged.head(10)

