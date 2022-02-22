'''
VMP 2022-02-21: 
just for checking files, does not do anything. 
'''
import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
import datetime, time
from tqdm import tqdm
pd.options.mode.chained_assignment = None  # default='warn'

# read stuff 
psych_paa = pd.read_csv("/work/50114/MAG/data/MAG/psychology_paper_author.csv")
psych_meta = pd.read_csv("/work/50114/MAG/data/MAG/psychology_paper_meta.csv")
psych_ref = pd.read_csv("/work/50114/MAG/data/MAG/psychology_reference.csv")

# check merge here (left vs. inner) -- not the issue
def check_teamsize_join(df_paa, df_meta, type):
    '''
    type: <str> inner or left 
    '''
    # do the merging
    paper_teamsize = df_paa.groupby('PaperId').size().reset_index(name='n_authors')
    df_meta_teamsize = df_meta.merge(paper_teamsize, on = 'PaperId', how = type)

    # print information
    divisor = 1000000
    print(f"{type}: {round(len(df_meta_teamsize)/divisor, 5)} million")

check_teamsize_join(psych_paa, psych_meta, "left")
check_teamsize_join(psych_paa, psych_meta, "inner")

# check how many papers are published in several fields of study
papers_duplicate = psych_meta.groupby('PaperId').size().reset_index(name = 'N').sort_values('N', ascending=False)
papers_duplicate.groupby('N').size() # very few duplications