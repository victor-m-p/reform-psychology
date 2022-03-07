'''
VMP 2022-02-22: 
has been superceeded by querry_control_match. 
needs to be deleted (when we have run new data through)
'''

import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
import datetime, time
from tqdm import tqdm
pd.options.mode.chained_assignment = None  # default='warn'
import os
import argparse 
from pathlib import Path

# read stuff 
psych_paa = pd.read_csv("/work/50114/MAG/data/raw/psychology_paper_author.csv")
psych_meta = pd.read_csv("/work/50114/MAG/data/raw/psychology_paper_meta_clean.csv")
psych_ref = pd.read_csv("/work/50114/MAG/data/raw/psychology_reference.csv")

# cleanup
# because some files in paa and ref are not in meta 
# those are files which either:
# (a) are not in "Papers.txt"
# (b) do not have FieldOfStudyId associated with PaperId
# (c) do not have any FieldOfStudyId of Level == 0. 
# they are all fine to leave out of this analysis.  
# this function gives us how many records we basically filter away in "get_metadata_papers" function on HPC.
# also: 
# (1) some files (few) in meta do not have Date, we also remove those. 

def clean_data(psych_meta, psych_paa, psych_ref): 
    # date cannot be na 
    psych_meta_clean = psych_meta[~psych_meta["Date"].isna()]

    # unique paperids from meta
    psych_meta_paperid = psych_meta_clean[["PaperId"]].drop_duplicates() 

    # clean paa
    psych_paa_clean = psych_paa.merge(psych_meta_paperid, on = 'PaperId', how = 'inner')
    print(f"paa raw: {len(psych_paa)}")
    print(f"paa clean: {len(psych_paa_clean)} \n")

    # clean ref 
    psych_ref_clean = psych_ref.merge(psych_meta_paperid, on = 'PaperId', how = 'inner')
    psych_meta_paperid = psych_meta_paperid.rename(columns={'PaperId': 'PaperReferenceId'})
    psych_ref_clean2 = psych_ref_clean.merge(psych_meta_paperid, on = 'PaperReferenceId', how = 'inner')
    print(f"ref raw: {len(psych_ref)}")
    print(f"ref clean (PaperId): {len(psych_ref_clean)}")
    print(f"ref clean (PaperReferenceId): {len(psych_ref_clean2)}")

    return psych_meta_clean, psych_paa_clean, psych_ref_clean2

psych_meta_clean, psych_paa_clean, psych_ref_clean = clean_data(psych_meta, psych_paa, psych_ref)

# function: get subset (period based on how long we need citation delay)
def get_subset(df, fos): 
    '''
    df: <pd.dataframe> dataframe (meta) to be cleaned
    fos: <str> field of study to match on
    '''
    filtered_df = df[
    (df["NormalizedName"] == f'{fos}') & 
    (df["DocType"] == 'Journal') & 
    (df["Date"] >= datetime.date(2010, 1, 1)) & 
    (df["Date"] <= datetime.date(2016, 1, 1))
    ]

    return filtered_df

# get our subset (psychology, Journal and between 2010-2021)
def get_keyword_subset(df_meta, df_paa, fos, keyword): 
    '''
    df_meta: <pd.dataframe> dataframe with meta-data (meta-data)
    df_paa: <pd.dataframe> dataframe with paper-author pairs
    fos: <str> field of study ("psychology" in the main analysis)
    keyword: <str> keyword to search for, e.g. "replicat"
    '''

    # fix Date 
    df_meta["Date"] = pd.to_datetime(df_meta["Date"]).dt.date
    
    # add team-size to meta-data (only for psychology)
    paper_teamsize = df_paa.groupby('PaperId').size().reset_index(name='n_authors')
    df_meta_teamsize = df_meta.merge(paper_teamsize, on = 'PaperId', how = 'inner') # some NA, why -- also here that it becomes float. 

    # filter data (baseline needs to come from this)
    filtered_df = get_subset(df_meta_teamsize, fos)

    # match on keyword & select columns
    df_replication = filtered_df.loc[filtered_df['PaperTitle'].str.contains(keyword, case=False)]
    df_replication = df_replication[["PaperId", "Date", "n_authors", "NormalizedName"]]

    # control data
    df_control = filtered_df[~filtered_df["PaperId"].isin(df_replication["PaperId"])]
    df_control = df_control[["PaperId", "Date", "n_authors", "NormalizedName"]]

    # print information 
    print(f"data for {fos} and {keyword} \n") 
    print(f"match: {len(df_replication)}, \ncontrol: {len(df_control)}")

    return df_meta_teamsize, df_replication, df_control

psych_meta_teamsize, psych_replication_2016, psych_control_2016 = get_keyword_subset(psych_meta_clean, psych_paa_clean, "psychology", "replicat")

# 783 observations that we want to match: 
## we should do a manual selection here of papers that are actually replications

def clean_records(df, paper_string):
    '''
    df: <pd.dataframe> either psych_replication_2016 or control_data_sub
    paper_string: <str> either "PaperIdExperiment" or "PaperIdControl" 
    
    returns: <pd.dataframe> 
    * no na 
    * number of authors as integer
    * renames PaperId column
    * sorts Date (needed for merge_asof() later) 
    * converts Date to pd.datetime() 
    ''' 

    # match records
    df["n_authors"] = df["n_authors"].astype(int)

    # rename PaperId 
    df = df.rename(columns = {'PaperId': paper_string})

    # sort frames
    df = df.sort_values('Date', ascending=True)

    # enforce datetime
    df["Date"] = pd.to_datetime(df["Date"])
    
    # return
    return df

psych_control_clean = clean_records(psych_control_2016, "PaperId_control")
psych_experiment_clean = clean_records(psych_replication_2016, "PaperId_experiment")

# merge_asof: trade-off --> 
## (1) we only get one match per record (i.e. one control per experimental)
## (2) we are not guaranteed the "best" match by looping. 
## (3) inefficient solution
def get_matches(d_exp, d_control):
    '''
    d_exp: <pd.dataframe> experimental condition
    d_control: <pd.dataframe> control condition
    ''' 
    
    # setup 
    d_loop = pd.DataFrame(
        columns = [
            "PaperId_experiment", 
            "Date",
            "n_authors",
            "NormalizedName",
            "PaperId_control"]
            )

    # loop 
    for i in tqdm(range(len(d_exp))):

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
        used_index = d_asof["PaperId_control"].item()    
        d_control = d_control[d_control["PaperId_control"] != used_index]

        # append 
        d_loop = d_loop.append(d_asof)
    
    # return 
    return(d_loop)

# pretty expensive computation now. 
psych_joined = get_matches(psych_experiment_clean, psych_control_clean)


# function: check how close our matches are & remove those more than 30 days apart 
def check_matching(psych_joined, psych_control):
    '''
    psych_joined: <pd.dataframe> the merged dataframe with date from "experiment"
    psych_control: <pd.dataframe> the cleaned control data. 
    ''' 

    # get dates from control 
    psych_control_dates = psych_control.rename(columns={'Date': 'Date_control'})[["PaperId_control", "Date_control"]]
    psych_joined_dates = psych_joined.merge(psych_control_dates, on = ["PaperId_control"], how = 'inner')
    psych_joined_dates = psych_joined_dates.rename(columns={'Date': 'Date_experiment'})
    psych_joined_dates = psych_joined_dates.assign(date_delta = lambda x: x["Date_experiment"] - x["Date_control"])

    # check stats (NB the study we are missing is a large-scale collaboration) 
    delay_equal_0 = len(psych_joined_dates[psych_joined_dates["date_delta"] == '0 days']) # by far majority has exact match
    delay_between_30 = len(psych_joined_dates[(psych_joined_dates["date_delta"] <= '30 days') & (psych_joined_dates["date_delta"] >= '-30 days')])
    delay_above_30 = len(psych_joined_dates[psych_joined_dates["date_delta"] > '30 days']) 
    delay_below_30 = len(psych_joined_dates[psych_joined_dates["date_delta"] < "-30 days"]) 

    # print matching statistics (day)
    print(f"delay with 30 days: {delay_between_30}")
    print(f"delay == 0 days: {delay_equal_0}")
    print(f"delay > 30 days: {delay_above_30}")
    print(f"delay < 30 days: {delay_below_30}")

    # check matching by year 
    psych_joined_dates["Year_experiment"] = [x.year for x in psych_joined_dates["Date_experiment"]]
    psych_joined_dates["Year_control"] = [x.year for x in psych_joined_dates["Date_control"]]
    psych_joined_dates = psych_joined_dates.assign(year_delta = lambda x: x["Year_experiment"] - x["Year_control"])
    year_equal_0 = len(psych_joined_dates[psych_joined_dates["year_delta"] == 0])
    year_above_0 = len(psych_joined_dates[psych_joined_dates["year_delta"] > 0])
    year_below_0 = len(psych_joined_dates[psych_joined_dates["year_delta"] < 0])

    # print matching statistics (year)
    print(f"pefect matching on year: {year_equal_0}")
    print(f"experiment year earlier than control: {year_above_0}")
    print(f"control year earlier than experiment: {year_below_0}")

    # remove studies more than 30 days appart 
    #psych_close_matches = psych_joined_dates[
    #    (psych_joined_dates["date_delta"] <= "30 days") & 
    #    (psych_joined_dates["date_delta"] >= "-30 days")
    #    ]

    # drop date_delta column
    psych_joined_dates = psych_joined_dates.drop(['date_delta', 'year_delta'], axis = 1)

    # return 
    return psych_joined_dates

# run function
psych_close_matches = check_matching(psych_joined, psych_control_clean)

# function: add identifier column & convert to long format 
def long_format(psych_matches):
    '''
    psych_matches: <pd.dataframe> the matched dataframe. 
    
    explanation: 
    adds a match-group (experiment-control), renames and then long-format
    ''' 

    # add identifier column for our matched samples 
    psych_matches['match_group'] = psych_matches.index + 1 
    number_matches = len(psych_matches) # 

    print(f"number of matched records: {number_matches}")

    ## -- to long format --
    # rename stuff (could go back and do it right from the start) 
    #psych_matches = psych_matches.rename(
    #    columns = {
    #        'PaperIdExperiment': 'PaperId_experiment',
    #        'PaperIdControl': 'PaperId_control',
    #        'DateExperiment': 'Date_experiment',
    #        'DateControl': 'Date_control',
    #        'YearExperiment'
    #        })

    # to long format 
    psych_long_format = pd.wide_to_long(
        psych_matches, 
        stubnames=['PaperId', 'Date', 'Year'], 
        i='match_group', 
        j='condition', 
        suffix='.*', 
        sep='_').reset_index()

    # print information
    psych_long_format_id = len(psych_long_format["PaperId"].drop_duplicates())
    print(f"number of unique id (should be 2x): {psych_long_format_id}")

    return psych_long_format

# run function (one fewer now: 391, because one record more than 30 days apart)
psych_long_format = long_format(psych_close_matches) 

#function: get citations for matched records:
# NB: our papers are PaperReferenceId (as they should). 
# NB: I have validated this on a small sample (i.e. that those that cite actually do cite). 
def get_citations(psych_ref, psych_long_format): 
    '''
    psych_ref: <pd.dataframe> the dataframe with PaperId and PaperReferenceId (our focus papers are PaperReferenceId)
    psych_long_format: <pd.dataframe> our matched records in long format 
    '''

    # rename columns of psych_ref
    psych_ref = psych_ref.rename(columns=
        {'PaperId': 'PaperCites',
        'PaperReferenceId': 'PaperId'}
    )

    # convert to dtypes that support NA (without converting)
    psych_long_format = psych_long_format.convert_dtypes() 
    psych_ref = psych_ref.convert_dtypes()

    # merge inner 
    psych_long_ref = psych_long_format.merge(psych_ref, on = 'PaperId', how = 'left')

    # print information
    psych_long_ref_len = len(psych_long_ref["PaperId"].drop_duplicates())
    print(f"psychology reference: {psych_long_ref_len}")

    # take out those of our records that have not been cited (psych_long_na)
    # they need different treatment from those that have been cited (psych_long_cited)
    psych_long_na = psych_long_ref[psych_long_ref["PaperCites"].isna()].drop('PaperCites', axis = 1)
    psych_long_cited = psych_long_ref[~psych_long_ref["PaperCites"].isna()]

    # get sense of how large each of these categories are 
    na_records = len(psych_long_na[["PaperId"]].drop_duplicates())
    cited_records = len(psych_long_cited[["PaperId"]].drop_duplicates())
    total_records = na_records + cited_records

    # print information
    print(f"total records: {total_records}")
    print(f"number of records without citations: {na_records}, {round((na_records/total_records)*100)}%")
    print(f"number of records with citations: {cited_records}, {round((cited_records/total_records)*100)}%")

    return psych_long_na, psych_long_cited

# run function
psych_long_na, psych_long_cited = get_citations(psych_ref_clean, psych_long_format)

# check whether all citations are after publication
## this is actually where we loose data. 
## we are lacking dates for a number of the papers that cite here. 
## we need to get all of those dates from Ucloud.
## but... we basically need paper-authors-date which is huge. 
## need to find a good solution to this. 
## or... we would need to have this on ucloud, which is also not a perfect solution.
## might be the best we can do though. 
## pretty annoying actually. 

def citation_delay(psych_meta, psych_long_cited, psych_long_na): 
    '''
    psych_meta: <pd.dataframe> psychology meta-data. 
    psych_long_cited: <pd.dataframe> psychology long format (only the cited papers)
    psych_long_na: <pd.dataframe> psychology long format (only non-cited papers)
    '''

    # convert date format
    psych_meta["Date"] = pd.to_datetime(psych_meta["Date"])

    # rename columns
    psych_dates = psych_meta.rename(columns={
        'PaperId': 'PaperCites',
        'Date': 'DateCites'})[["PaperCites", "DateCites"]]

    # ensures proper format (can handle NA within various dtypes)
    psych_dates = psych_dates.convert_dtypes()

    # merge with psych_cited
    psych_long_merged = psych_long_cited.merge(psych_dates, on = ['PaperCites'], how = 'inner')

    # print information (we do lose some here, should be because of NaN in date?
    print(f"psychology before merge: {len(psych_long_cited)}")
    print(f"psychology after merge: {len(psych_long_merged)}")

    # assign time-gap to filter based on (to create c_5)
    psych_long_merged = psych_long_merged.assign(
        time_gap = lambda x: x["DateCites"] - x["Date"],
        time_gap_int = lambda x: x["time_gap"].dt.days).drop('time_gap', axis = 1)

    # test whether any "negative" days (only very few) & how many after 5 years
    citations_below_0_days = len(psych_long_merged[psych_long_merged["time_gap_int"] < 0]) 
    citations_above_5_years = len(psych_long_merged[psych_long_merged["time_gap_int"] > 1825]) 
    citations_within_5_years = len(psych_long_merged) - citations_below_0_days - citations_above_5_years

    # print information
    print(f"number of citations between 0 days and 5 years: {citations_within_5_years}")
    print(f"number of citations after less than 0 days: {citations_below_0_days}")
    print(f"number of citations after more than 5 years: {citations_above_5_years}")

    # filter out those that are more than 5 years after (365 * 5 = 1825 days) and less than 0 days. 
    psych_inside_five = psych_long_merged[(psych_long_merged["time_gap_int"] <= 1825) & (psych_long_merged["time_gap_int"] >= 0)] 
    psych_outside_five = psych_long_merged[(psych_long_merged["time_gap_int"] > 1825) | (psych_long_merged["time_gap_int"] < 0)]

    # print information
    print(f"psychology: {len(psych_long_merged)}")
    print(f"inside: {len(psych_inside_five)}")
    print(f"outside: {len(psych_outside_five)}")

    # find those that are only in "outside" & not in "inside" (i.e. cited, but not within frame)
    psych_outside_five = psych_outside_five.drop(['PaperCites', 'DateCites', 'time_gap_int'], axis = 1).drop_duplicates()
    psych_inside_five_id = psych_inside_five[["PaperId"]].drop_duplicates()
    psych_inside_five_lst = psych_inside_five_id["PaperId"].tolist()
    psych_outside_five_only = psych_outside_five[~psych_outside_five["PaperId"].isin(psych_inside_five_lst)]

    # gather with the other "no citations": 
    psych_outside_five = pd.concat([psych_long_na, psych_outside_five_only])

    # print information
    psych_outside_five_len = len(psych_outside_five["PaperId"].drop_duplicates())
    psych_inside_five_len = len(psych_inside_five["PaperId"].drop_duplicates())
    total_len = psych_outside_five_len + psych_inside_five_len
    print(f"total unique papers: {total_len}") # slightly fewer than what we should have
    print(f"papers with citations inside five years: {psych_inside_five_len}")
    print(f"papers without citations inside five years: {psych_outside_five_len}")
    return psych_outside_five, psych_inside_five

# run function: 
## almost as many citations after the timedelta of 5 years (slightly surprising). 
psych_outside_five, psych_inside_five = citation_delay(psych_meta_clean, psych_long_cited, psych_long_na)

# function: convert Date to "days_after_2010" variable
def dates_after_2010(df, start_date):
    '''
    df: <pandas.dataframe> 
    start_date: datetime.date() 
    ''' 
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    df = df.assign(days_after_2010 = lambda x: (x["Date"] - start_date).dt.days)
    return df 

psych_inside_five = dates_after_2010(psych_inside_five, datetime.date(2010, 1, 1))
psych_outside_five = dates_after_2010(psych_outside_five, datetime.date(2010, 1, 1))

def clean_columns(psych_inside_five, psych_outside_five): 
    '''
    psych_inside_five: <pd.dataframe> long-format matched records (with citations)
    psych_outside_five: <pd.dataframe> long-format matched records (no citations)

    explanation: 
    creates the c_5 variable.
    drops unused columns.
    concatenates the cited records and the non-cited records.

    returns: 
    psych_ready: <pd.dataframe> the processed & ready data
    '''

    # create c_5 variable
    df_c5 = psych_inside_five.groupby('PaperId').size().reset_index(name = 'c_5')

    # remove unused columns and merge c_5 back (also NormalizedName for now)
    psych_inside_five_clean = psych_inside_five.drop(['NormalizedName', 'PaperCites', 'DateCites', 'time_gap_int', 'Date'], axis = 1).drop_duplicates()
    psych_outside_five_clean = psych_outside_five.drop(['NormalizedName', 'Date'], axis = 1).drop_duplicates()
    
    # check data and print information
    length_na = len(psych_outside_five_clean)
    length_cited = len(psych_inside_five_clean)
    print(f"total records: {length_na + length_cited}")
    print(f"number of non-cited records: {length_na}")
    print(f"number of cited records: {length_cited}")

    # merge c_5 back in to the data 
    psych_inside_five_c5 = psych_inside_five_clean.merge(df_c5, on = 'PaperId', how = 'inner')

    # fix format and concat
    psych_outside_five_clean["c_5"] = 0 # zero citations 
    psych_ready = pd.concat([psych_inside_five_c5, psych_outside_five_clean])
    psych_ready = psych_ready.sort_values('match_group', ascending = True).reset_index(drop=True)
    return psych_ready

# run file 
psych_ready = clean_columns(psych_inside_five, psych_outside_five)

# write final file # 
psych_ready.to_csv("/work/50114/MAG/data/modeling/psych_replication_matched.csv", index = False) 

def main(inpath, field, querry, outpath): 
    # read files
    df_paa = pd.read_csv(f"{inpath}/{field}_paper_author.csv")
    df_meta = pd.read_csv(f"{inpath}/{field}_paper_meta_clean.csv")
    df_ref = pd.read_csv(f"{inpath}/{field}_reference.csv")



if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--inpath", required=True, type=str, help="path to folder with files")
    ap.add_argument("-f", "--field", required=True, type=str, help="field of study, e.g. psychology")
    ap.add_argument("-q", "--querry", required=True, type=str, help="querry to search for in titles, e.g. replicat")
    ap.add_argument("-o", "--outpath", required=True, type=str, help="path to folder for output csv")
    args = vars(ap.parse_args())

    main(inpath = args['inpath'], outpath = args['outpath'])