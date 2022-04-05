'''
VMP 2022-04-02: 
Check the data  we are actually modeling: 
* Replication (FoS)
* Replication (Query)
* Reproducibility (FoS)
* Open Science (FoS)

Returns: 
* Number of total records (groups = records/2) -- (2005, 2015)
* Sample of 20% of studies for each of the three categories (SI) 
* Manual check of top-cited articles (c_5 > 100). 
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
df_reproducibility = pd.read_csv("/work/50114/MAG/data/modeling/psychology_reproducibility_matched.csv")
df_openscience = pd.read_csv("/work/50114/MAG/data/modeling/psychology_openscience_matched.csv")
df_replicat = pd.read_csv("/work/50114/MAG/data/modeling/psychology_replicat_matched.csv")

# outpath
outpath = "/work/50114/MAG/data/EDA/"

# gather numbers 
length_replication = len(df_replication) 
length_reproducibility = len(df_reproducibility)
length_openscience = len(df_openscience)
length_replicat = len(df_replicat)

# gather data 
d_size = pd.DataFrame({
    'Group': [
        'replication_fos',
        'reproducibility_fos',
        'openscience_fos',
        'replication_query'], 
    'N': [
        length_replication, 
        length_reproducibility,
        length_openscience, 
        length_replicat
    ],
    'Matched': [
        int(length_replication/2), 
        int(length_reproducibility/2),
        int(length_openscience/2),
        int(length_replicat/2)
    ]
})

# write 
d_size.to_csv(f"{outpath}number_of_records.csv", index = False)

# manual subsets 
def get_experiment(d, n = 20): 
    '''
    d: <pd.dataframe> 
    '''
    d = d[d["condition"] == "experiment"]
    d = d[["Year", "PaperTitle"]]
    d = d.sample(n = 20, random_state = 5)
    d = d.sort_values('Year', ascending=True)
    return d

# generate subset 
df_replication_exp = get_experiment(df_replication) 
df_reproducibility_exp = get_experiment(df_reproducibility)
df_openscience_exp = get_experiment(df_openscience)
df_replicat_exp = get_experiment(df_replicat)

# write to latex (consider ordering by year)
def write_latex(d, outname): 
    '''
    d: <pd.dataframe> 
    outname: <str> 
    '''

    d_latex = d.to_latex(
        multicolumn=True, 
        header=True, 
        index_names=False,
        index=False, 
        column_format='p{1cm}|p{13cm}'
        )

    with open(f"{outname}.txt", 'w') as f: 
        f.write(d_latex)

# write latex tables to .txt
write_latex(
    d = df_replication_exp, 
    outname = f"{outpath}replication_fos_20"
)

write_latex(
    d = df_reproducibility_exp,
    outname = f"{outpath}reproducibility_fos_20"
)

write_latex(
    d = df_openscience_exp,
    outname = f"{outpath}openscience_fos_20"
)

write_latex(
    d = df_replicat_exp,
    outname = f"{outpath}replication_query_20"
)

# check the large studies (only for replication_fos)
def get_outliers(d, cutoff): 
    '''
    d: <pd.dataframe> 
    cutoff: <int> only studies with higher c5 than this
    '''

    d = d[d["c_5"] >= cutoff]
    d = d[["condition", "Year", "PaperTitle", "c_5", "n_authors"]]
    d = d.sort_values('c_5', ascending=False)
    return d


# get studies 
replication_fos_hit = get_outliers(df_replication, 100)
replication_query_hit = get_outliers(df_replicat, 100)
reproducibility_fos_hit = get_outliers(df_reproducibility, 100)

# check them 
pd.set_option('display.max_colwidth', None)
replication_fos_hit # a lot of this is survey data
replication_query_hit # many of these are some survey, some are review and some good (e.g. manylabs)
reproducibility_fos_hit

# save them 
replication_fos_hit.to_csv(f"{outpath}replication_fos_above_100.csv", index = False)
replication_query_hit.to_csv(f"{outpath}replication_query_above_100.csv", index = False)
reproducibility_fos_hit.to_csv(f"{outpath}reproducibility_fos_above_100.csv", index = False)

# comment
## we do seem to have an issue with: 
### 1. conceptual/review pieces that are really popular 
##### --> does skew it somewhat (we know something about review, right?)
##### --> they talk about reviews in small/large teams at least
### 2. the national comorbidity survery replication appears multiple times (i.e. different years) & is cited a lot.
##### --> this is not necessarily a problem 
### 3. we do also capture some of what we are actually interested in
##### ---> e.g. ManyLabs (index: 1718) & ADOS (index: 603) & registered replication (index: 2003)
### 4. good that we regularize with random effects to make it more robust. 

# check overlap of replication_fos and replication_query
## potentially 