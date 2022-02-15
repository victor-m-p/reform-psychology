import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
import datetime, time
#from datetime import datetime, timedelta
pd.options.mode.chained_assignment = None  # default='warn'

# read stuff 
psych_paa = pd.read_csv("/work/50114/MAG/data/MAG/psychology_paper_author.csv")
psych_meta = pd.read_csv("/work/50114/MAG/data/MAG/psychology_paper_meta.csv")
psych_ref = pd.read_csv("/work/50114/MAG/data/MAG/psychology_reference.csv")

# fix date format
psych_meta["Date"] = pd.to_datetime(psych_meta["Date"]).dt.date

# add team-size to meta-data (only for psychology)
paper_teamsize = psych_paa.groupby('PaperId').size().reset_index(name='n_authors')
psych_meta_teamsize = psych_meta.merge(paper_teamsize, on = 'PaperId', how = 'left') # some NA, why -- also here that it becomes float. 


# get our subset (psychology, Journal and between 2010-2021)
def get_subset(df, fos): 
    filtered_df = df[
        (df["NormalizedName"] == f'{fos}') & 
        (df["DocType"] == 'Journal') & 
        (df["Date"] >= datetime.date(2010, 1, 1)) & 
        (df["Date"] <= datetime.date(2021, 1, 1))
        ]
    return filtered_df

psych_meta_sub = get_subset(psych_meta_teamsize, "psychology")
psych_paperid_sub = psych_meta_sub[["PaperId"]].drop_duplicates()

# find papers that mention "replicat" & are before 2016. 
def get_replication(df, df_sub): 
    df = df.merge(df_sub, on = 'PaperId', how = 'inner') # only from selection (could also be done smarter). 
    df_replication = df.loc[df['PaperTitle'].str.contains("replicat", case=False)]
    df_replication = df_replication[['PaperId', 'Date', 'n_authors', 'NormalizedName']]
    df_replication_before2016 = df_replication[df_replication["Date"] <= datetime.date(2016, 1, 1)]
    return df_replication_before2016

psych_replication_2016 = get_replication(psych_meta_teamsize, psych_paperid_sub)

# 392 observations that we want to match: 
# (0) we should do a manual selection here of papers that are actually replications
# --- setting that aside for the moment --- 
# (1) create data-set (meta) without these papers.
# (2) remove all papers that have some "null" aspect. 
# (3) match based on team-size and date between the two frames

# control data we can sample from 
control_data = psych_meta_teamsize[~psych_meta_teamsize["PaperId"].isin(psych_replication_2016.PaperId)]
control_data_sub = get_subset(control_data, "psychology")
control_data_sub = control_data_sub[["PaperId", "Date", "n_authors", "NormalizedName"]]

# remove all papers that have "null" aspects 
# actually more than 10% have null, so we need to check this (well, maybe??)
psych_experiment_clean = psych_replication_2016.dropna()
psych_control_clean = control_data_sub.dropna()

# now we match 
# question is 
# (1) whether we even need to - and 
# (2) whether we want as many "controls" as possible (probably, yes). 
psych_experiment_clean["n_authors"] = psych_experiment_clean["n_authors"].astype(int)
psych_control_clean["n_authors"] = psych_control_clean["n_authors"].astype(int)

psych_control_clean.isnull().sum()
psych_experiment_clean.isnull().sum()

# rename stuff
psych_experiment_clean = psych_experiment_clean.rename(columns = {'PaperId': 'PaperIdExperiment'})
psych_control_clean = psych_control_clean.rename(columns = {'PaperId': 'PaperIdControl'})

# convert to month?
## potentially "tolerance" parameter
tol = pd.Timedelta("10 days")

## sort frames
psych_experiment_clean = psych_experiment_clean.sort_values('Date', ascending=True)
psych_control_clean = psych_control_clean.sort_values('Date', ascending=True)

## needs to be date
psych_control_clean["Date"] = pd.to_datetime(psych_control_clean["Date"])
psych_experiment_clean["Date"] = pd.to_datetime(psych_experiment_clean["Date"])

# merge_asof: trade-off --> 
## (1) we only get one match per record (experiment condition)
## (2) for some we get the same match (control) for more than one record (experiment condition)
psych_joined = pd.merge_asof(
    psych_experiment_clean, 
    psych_control_clean, # this is the "Date" we will get 
    on = 'Date', # can be "asof" (close match) 
    by = ['n_authors', 'NormalizedName'], # has to be equivalent
    direction = 'nearest')

# now we check how close these actually are: 

##### try the other way ##### 
psych_control_dates = psych_control_clean.rename(columns={'Date': 'DateControl'})[["PaperIdControl", "DateControl"]]
psych_joined_dates = psych_joined.merge(psych_control_dates, on = ["PaperIdControl"], how = 'inner')
psych_joined_dates = psych_joined_dates.rename(columns={'Date': 'DateExperiment'})
psych_joined_dates = psych_joined_dates.assign(date_delta = lambda x: x.DateExperiment - x.DateControl)

## check stats (NB the study we are missing is a large-scale collaboration)
## could also match approximately on number of authors & then approximately on date & then take inner. 
len(psych_joined_dates[psych_joined_dates["date_delta"] == '0 days']) # by far majority has exact match
len(psych_joined_dates[psych_joined_dates["date_delta"] > '30 days']) # 0 more than 30 days before
len(psych_joined_dates[psych_joined_dates["date_delta"] < "-30 days"]) # 1 more than 30 days after 

## remove studies more than 30 days appart 
psych_close_matches = psych_joined_dates[
    (psych_joined_dates["date_delta"] <= "30 days") & 
    (psych_joined_dates["date_delta"] >= "-30 days")
    ]

## reformat the data
# drop date_delta column
psych_close_matches = psych_close_matches.drop(['date_delta'], axis = 1)

# add identifier column for our matched samples 
psych_close_matches['match_group'] = psych_close_matches.index + 1 
psych_close_matches # 391 is the number we care about --> NB: we have some controls that are the same 

## -- to long format --
# rename stuff (could go back and do it right from the start) 
psych_close_matches = psych_close_matches.rename(
    columns = {
        'PaperIdExperiment': 'PaperId_experiment',
        'PaperIdControl': 'PaperId_control',
        'DateExperiment': 'Date_experiment',
        'DateControl': 'Date_control'
        })

# to long format 
psych_long_format = pd.wide_to_long(
    psych_close_matches, 
    stubnames=['PaperId', 'Date'], 
    i='match_group', 
    j='condition', 
    suffix='.*', 
    sep='_').reset_index()

## calculate c_5* : 
# NB: our papers are PaperReferenceId (as they should). 
# NB: I have validated this on a small sample (i.e. that those that cita actually do cite). 
psych_ref = psych_ref.rename(columns=
    {'PaperId': 'PaperCites',
    'PaperReferenceId': 'PaperId'}
)

## do it with full data
# convert to dtypes that support NA (without converting)
psych_long_format = psych_long_format.convert_dtypes() 
psych_ref = psych_ref.convert_dtypes()

# merge inner 
psych_long_ref = psych_long_format.merge(psych_ref, on = 'PaperId', how = 'left')

### take those that are NA out ### 
psych_long_na = psych_long_ref[psych_long_ref["PaperCites"].isna()].drop('PaperCites', axis = 1)
psych_long_cited = psych_long_ref[~psych_long_ref["PaperCites"].isna()]

## for now just date (not doctype, normalizedname)
psych_meta["Date"] = pd.to_datetime(psych_meta["Date"])
psych_dates = psych_meta.rename(columns={
    'PaperId': 'PaperCites',
    'Date': 'DateCites'})[["PaperCites", "DateCites"]]
psych_dates = psych_dates.convert_dtypes()

## bind 
psych_long_cited = psych_long_cited.merge(psych_dates, on = ['PaperCites'], how = 'inner')

## check whether all citations are after publication
psych_long_cited = psych_long_cited.assign(
    time_gap = lambda x: x["DateCites"] - x["Date"],
    time_gap_int = lambda x: x["time_gap"].dt.days).drop('time_gap', axis = 1)

## test whether any "negative" days (only very few) & how many after 5 years
len(psych_long_cited[psych_long_cited["time_gap_int"] < 0])
len(psych_long_cited[psych_long_cited["time_gap_int"] > 1825]) # actually a lot of late references

## filter out those that are more than 5 years after (365 * 5 = 1825 days)
psych_inside_five = psych_long_cited[psych_long_cited["time_gap_int"] <= 1825] # becomes the new main frame 
psych_outside_five = psych_long_cited[psych_long_cited["time_gap_int"] > 1825]

# find those that are only in "outside" & not in "inside" (i.e. cited, but not within frame)
psych_outside_five = psych_outside_five.drop(['PaperCites', 'DateCites', 'time_gap_int'], axis = 1).drop_duplicates()
psych_inside_five_id = psych_inside_five[["PaperId"]].drop_duplicates()
psych_inside_five_lst = psych_inside_five_id["PaperId"].tolist()
psych_outside_five_only = psych_outside_five[~psych_outside_five["PaperId"].isin(psych_inside_five_lst)]

# gather with the other "no citations": 
psych_long_na = pd.concat([psych_long_na, psych_outside_five_only])

### for both psych_long_na & psych_long_cited
def dates_after_2010(df, start_date):
    '''
    df: <pandas.dataframe> 
    start_date: datetime.date() 
    ''' 
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    df = df.assign(days_after_2010 = lambda x: (x["Date"] - start_date).dt.days)
    return df 

psych_inside_five = dates_after_2010(psych_inside_five, datetime.date(2010, 1, 1))
psych_long_na = dates_after_2010(psych_long_na, datetime.date(2010, 1, 1))

# write this file for plotting # 
#df_citations.to_csv()

## convert to integer 
df_c5 = psych_inside_five.groupby('PaperId').size().reset_index(name = 'c_5')

# remove unused columns and merge c_5 back (also NormalizedName for now)
psych_inside_five_clean = psych_inside_five.drop(['NormalizedName', 'PaperCites', 'DateCites', 'time_gap_int', 'Date'], axis = 1).drop_duplicates()
psych_long_na = psych_long_na.drop(['NormalizedName', 'Date'], axis = 1)
length_na = len(psych_long_na)
length_cited = len(psych_inside_five_clean)

## check whether equal to original - should be 372 ## 
int((length_na + length_cited) / 2)

#### merge c_5 back in to the data ####
psych_long_c5 = psych_inside_five_clean.merge(df_c5, on = 'PaperId', how = 'inner')

# fix format and concat
psych_long_na["c_5"] = 0 # zero citations 
psych_ready = pd.concat([psych_long_c5, psych_long_na])
psych_ready = psych_ready.sort_values('match_group', ascending = True).reset_index(drop=True)

# write final file # 
psych_ready.to_csv("/work/50114/MAG/data/modeling/psych_replication_matched.csv", index = False) 