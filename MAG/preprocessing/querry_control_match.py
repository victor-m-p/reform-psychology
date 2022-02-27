'''
VMP 2022-02-22: 
Main document for matching & calculating c_5 and date-delay. 
Tricky things about matching: 
1) loop strategy does not ensure best match
2) would be good to match approximately on two columns rather than only on one (makes it hard to match those with high n. authors)

For now based on Journal only and 2010-2021. 
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
def clean_data(df_meta, df_paa, df_ref): 
    # date cannot be na 
    df_meta_clean = df_meta[~df_meta["Date"].isna()]

    # unique paperids from meta
    df_meta_paperid = df_meta_clean[["PaperId"]].drop_duplicates() 

    # clean paa
    df_paa_clean = df_paa.merge(df_meta_paperid, on = 'PaperId', how = 'inner')
    print(f"paa raw: {len(df_paa)}")
    print(f"paa clean: {len(df_paa_clean)} \n")

    # clean ref 
    df_ref_clean = df_ref.merge(df_meta_paperid, on = 'PaperId', how = 'inner')
    df_meta_paperid = df_meta_paperid.rename(columns={'PaperId': 'PaperReferenceId'})
    df_ref_clean2 = df_ref_clean.merge(df_meta_paperid, on = 'PaperReferenceId', how = 'inner')
    print(f"ref raw: {len(df_ref)}")
    print(f"ref clean (PaperId): {len(df_ref_clean)}")
    print(f"ref clean (PaperReferenceId): {len(df_ref_clean2)}")

    return df_meta_clean, df_paa_clean, df_ref_clean2

# function: get subset (period based on how long we need citation delay)
def get_subset(df, fos): 
    '''
    df: <pd.dataframe> dataframe (meta) to be cleaned
    fos: <str> field of study to match on
    '''

    # need to account for this one 
    if fos == "politicalscience":
        fos = "political science"

    filtered_df = df[
    (df["NormalizedName"] == f'{fos}') & 
    (df["DocType"] == 'Journal') & # this needs to be changed to Journal and Conference when we get the new data. 
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
    df_keyword = filtered_df.loc[filtered_df['PaperTitle'].str.contains(keyword, case=False)]
    df_keyword = df_keyword[["PaperId", "Date", "n_authors", "NormalizedName"]]

    # control data
    df_control = filtered_df[~filtered_df["PaperId"].isin(df_keyword["PaperId"])]
    df_control = df_control[["PaperId", "Date", "n_authors", "NormalizedName"]]

    # print information 
    print(f"data for {fos} and {keyword} \n") 
    print(f"match: {len(df_keyword)}, \ncontrol: {len(df_control)}")

    return df_keyword, df_control # df_meta_teamsize


## we should do a manual selection here of papers that are actually replications
def clean_records(df, paper_string):
    '''
    df: <pd.dataframe> either e.g. psych_replication_2016 or control_data_sub
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


# function: check how close our matches are & remove those more than 30 days apart 
def check_matching(df_joined, df_control):
    '''
    df_joined: <pd.dataframe> the merged dataframe with date from "experiment"
    df_control: <pd.dataframe> the cleaned control data. 
    ''' 

    # get dates from control 
    df_control_dates = df_control.rename(columns={'Date': 'Date_control'})[["PaperId_control", "Date_control"]]
    df_joined_dates = df_joined.merge(df_control_dates, on = ["PaperId_control"], how = 'inner')
    df_joined_dates = df_joined_dates.rename(columns={'Date': 'Date_experiment'})
    df_joined_dates = df_joined_dates.assign(date_delta = lambda x: x["Date_experiment"] - x["Date_control"])

    # check stats (NB the study we are missing is a large-scale collaboration) 
    delay_equal_0 = len(df_joined_dates[df_joined_dates["date_delta"] == '0 days']) # by far majority has exact match
    delay_between_30 = len(df_joined_dates[(df_joined_dates["date_delta"] <= '30 days') & (df_joined_dates["date_delta"] >= '-30 days')])
    delay_above_30 = len(df_joined_dates[df_joined_dates["date_delta"] > '30 days']) 
    delay_below_30 = len(df_joined_dates[df_joined_dates["date_delta"] < "-30 days"]) 

    # print matching statistics (day)
    print(f"delay with 30 days: {delay_between_30}")
    print(f"delay == 0 days: {delay_equal_0}")
    print(f"delay > 30 days: {delay_above_30}")
    print(f"delay < 30 days: {delay_below_30}")

    # check matching by year 
    df_joined_dates["Year_experiment"] = [x.year for x in df_joined_dates["Date_experiment"]]
    df_joined_dates["Year_control"] = [x.year for x in df_joined_dates["Date_control"]]
    df_joined_dates = df_joined_dates.assign(year_delta = lambda x: x["Year_experiment"] - x["Year_control"])
    year_equal_0 = len(df_joined_dates[df_joined_dates["year_delta"] == 0])
    year_above_0 = len(df_joined_dates[df_joined_dates["year_delta"] > 0])
    year_below_0 = len(df_joined_dates[df_joined_dates["year_delta"] < 0])

    # print matching statistics (year)
    print(f"pefect matching on year: {year_equal_0}")
    print(f"experiment year earlier than control: {year_above_0}")
    print(f"control year earlier than experiment: {year_below_0}")

    # remove studies more than 30 days appart 
    #df_close_matches = df_joined_dates[
    #    (df_joined_dates["date_delta"] <= "30 days") & 
    #    (df_joined_dates["date_delta"] >= "-30 days")
    #    ]

    # drop date_delta column
    df_joined_dates = df_joined_dates.drop(['date_delta', 'year_delta'], axis = 1)

    # return 
    return df_joined_dates


# function: add identifier column & convert to long format 
def long_format(df_matches):
    '''
    df_matches: <pd.dataframe> the matched dataframe. 
    
    explanation: 
    adds a match-group (experiment-control), renames and then long-format
    ''' 

    # add identifier column for our matched samples 
    df_matches['match_group'] = df_matches.index + 1 
    number_matches = len(df_matches) # 

    print(f"number of matched records: {number_matches}")

    ## -- to long format --
    # rename stuff (could go back and do it right from the start) 
    #df_matches = df_matches.rename(
    #    columns = {
    #        'PaperIdExperiment': 'PaperId_experiment',
    #        'PaperIdControl': 'PaperId_control',
    #        'DateExperiment': 'Date_experiment',
    #        'DateControl': 'Date_control',
    #        'YearExperiment'
    #        })

    # to long format 
    df_long_format = pd.wide_to_long(
        df_matches, 
        stubnames=['PaperId', 'Date', 'Year'], 
        i='match_group', 
        j='condition', 
        suffix='.*', 
        sep='_').reset_index()

    # print information
    df_long_format_id = len(df_long_format["PaperId"].drop_duplicates())
    print(f"number of unique id (should be 2x): {df_long_format_id}")

    return df_long_format

#function: get citations for matched records:
# NB: our papers are PaperReferenceId (as they should). 
# NB: I have validated this on a small sample (i.e. that those that cite actually do cite). 
def get_citations(df_ref, df_long_format): 
    '''
    df_ref: <pd.dataframe> the dataframe with PaperId and PaperReferenceId (our focus papers are PaperReferenceId)
    df_long_format: <pd.dataframe> our matched records in long format 
    '''

    # rename columns of df_ref
    df_ref = df_ref.rename(columns=
        {'PaperId': 'PaperCites',
        'PaperReferenceId': 'PaperId'}
    )

    # convert to dtypes that support NA (without converting)
    df_long_format = df_long_format.convert_dtypes() 
    df_ref = df_ref.convert_dtypes()

    # merge inner 
    df_long_ref = df_long_format.merge(df_ref, on = 'PaperId', how = 'left')

    # print information
    df_long_ref_len = len(df_long_ref["PaperId"].drop_duplicates())
    print(f"dfology reference: {df_long_ref_len}")

    # take out those of our records that have not been cited (df_long_na)
    # they need different treatment from those that have been cited (df_long_cited)
    df_long_na = df_long_ref[df_long_ref["PaperCites"].isna()].drop('PaperCites', axis = 1)
    df_long_cited = df_long_ref[~df_long_ref["PaperCites"].isna()]

    # get sense of how large each of these categories are 
    na_records = len(df_long_na[["PaperId"]].drop_duplicates())
    cited_records = len(df_long_cited[["PaperId"]].drop_duplicates())
    total_records = na_records + cited_records

    # print information
    print(f"total records: {total_records}")
    print(f"number of records without citations: {na_records}, {round((na_records/total_records)*100)}%")
    print(f"number of records with citations: {cited_records}, {round((cited_records/total_records)*100)}%")

    return df_long_na, df_long_cited


# check whether all citations are after publication
## this is actually where we loose data. 
## we are lacking dates for a number of the papers that cite here. 
## we need to get all of those dates from Ucloud.
## but... we basically need paper-authors-date which is huge. 
## need to find a good solution to this. 
## or... we would need to have this on ucloud, which is also not a perfect solution.
## might be the best we can do though. 
## pretty annoying actually. 

def citation_delay(df_meta, df_long_cited, df_long_na): 
    '''
    df_meta: <pd.dataframe> e.g. psychology meta-data. 
    df_long_cited: <pd.dataframe> e.g. psychology long format (only the cited papers)
    df_long_na: <pd.dataframe> e.g. psychology long format (only non-cited papers)
    '''

    # convert date format
    df_meta["Date"] = pd.to_datetime(df_meta["Date"])

    # rename columns
    df_dates = df_meta.rename(columns={
        'PaperId': 'PaperCites',
        'Date': 'DateCites'})[["PaperCites", "DateCites"]]

    # ensures proper format (can handle NA within various dtypes)
    df_dates = df_dates.convert_dtypes()

    # merge with df_cited
    df_long_merged = df_long_cited.merge(df_dates, on = ['PaperCites'], how = 'inner')

    # print information (we do lose some here, should be because of NaN in date?
    print(f"dfology before merge: {len(df_long_cited)}")
    print(f"dfology after merge: {len(df_long_merged)}")

    # assign time-gap to filter based on (to create c_5)
    df_long_merged = df_long_merged.assign(
        time_gap = lambda x: x["DateCites"] - x["Date"],
        time_gap_int = lambda x: x["time_gap"].dt.days).drop('time_gap', axis = 1)

    # test whether any "negative" days (only very few) & how many after 5 years
    citations_below_0_days = len(df_long_merged[df_long_merged["time_gap_int"] < 0]) 
    citations_above_5_years = len(df_long_merged[df_long_merged["time_gap_int"] > 1825]) 
    citations_within_5_years = len(df_long_merged) - citations_below_0_days - citations_above_5_years

    # print information
    print(f"number of citations between 0 days and 5 years: {citations_within_5_years}")
    print(f"number of citations after less than 0 days: {citations_below_0_days}")
    print(f"number of citations after more than 5 years: {citations_above_5_years}")

    # filter out those that are more than 5 years after (365 * 5 = 1825 days) and less than 0 days. 
    df_inside_five = df_long_merged[(df_long_merged["time_gap_int"] <= 1825) & (df_long_merged["time_gap_int"] >= 0)] 
    df_outside_five = df_long_merged[(df_long_merged["time_gap_int"] > 1825) | (df_long_merged["time_gap_int"] < 0)]

    # print information
    print(f"total: {len(df_long_merged)}")
    print(f"inside: {len(df_inside_five)}")
    print(f"outside: {len(df_outside_five)}")

    # find those that are only in "outside" & not in "inside" (i.e. cited, but not within frame)
    df_outside_five = df_outside_five.drop(['PaperCites', 'DateCites', 'time_gap_int'], axis = 1).drop_duplicates()
    df_inside_five_id = df_inside_five[["PaperId"]].drop_duplicates()
    df_inside_five_lst = df_inside_five_id["PaperId"].tolist()
    df_outside_five_only = df_outside_five[~df_outside_five["PaperId"].isin(df_inside_five_lst)]

    # gather with the other "no citations": 
    df_outside_five = pd.concat([df_long_na, df_outside_five_only])

    # print information
    df_outside_five_len = len(df_outside_five["PaperId"].drop_duplicates())
    df_inside_five_len = len(df_inside_five["PaperId"].drop_duplicates())
    total_len = df_outside_five_len + df_inside_five_len
    print(f"total unique papers: {total_len}") # slightly fewer than what we should have
    print(f"papers with citations inside five years: {df_inside_five_len}")
    print(f"papers without citations inside five years: {df_outside_five_len}")
    return df_outside_five, df_inside_five


# function: convert Date to "days_after_2010" variable
def days_after_2010(df, start_date):
    '''
    df: <pandas.dataframe> 
    start_date: datetime.date() 
    ''' 
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    df = df.assign(days_after_2010 = lambda x: (x["Date"] - start_date).dt.days)
    return df 

def clean_columns(df_inside_five, df_outside_five): 
    '''
    df_inside_five: <pd.dataframe> long-format matched records (with citations)
    df_outside_five: <pd.dataframe> long-format matched records (no citations)

    explanation: 
    creates the c_5 variable.
    drops unused columns.
    concatenates the cited records and the non-cited records.

    returns: 
    df_ready: <pd.dataframe> the processed & ready data
    '''

    # create c_5 variable
    df_c5 = df_inside_five.groupby('PaperId').size().reset_index(name = 'c_5')

    # remove unused columns and merge c_5 back (also NormalizedName for now)
    df_inside_five_clean = df_inside_five.drop(['NormalizedName', 'PaperCites', 'DateCites', 'time_gap_int', 'Date'], axis = 1).drop_duplicates()
    df_outside_five_clean = df_outside_five.drop(['NormalizedName', 'Date'], axis = 1).drop_duplicates()
    
    # check data and print information
    length_na = len(df_outside_five_clean)
    length_cited = len(df_inside_five_clean)
    print(f"total records: {length_na + length_cited}")
    print(f"number of non-cited records: {length_na}")
    print(f"number of cited records: {length_cited}")

    # merge c_5 back in to the data 
    df_inside_five_c5 = df_inside_five_clean.merge(df_c5, on = 'PaperId', how = 'inner')

    # fix format and concat
    df_outside_five_clean["c_5"] = 0 # zero citations 
    df_ready = pd.concat([df_inside_five_c5, df_outside_five_clean])
    df_ready = df_ready.sort_values('match_group', ascending = True).reset_index(drop=True)
    return df_ready

# main
def main(inpath, field, querry, outpath): 

    # read files
    df_paa = pd.read_csv(f"{inpath}/{field}_paper_author.csv")
    df_meta = pd.read_csv(f"{inpath}/{field}_paper_meta_clean.csv")
    df_ref = pd.read_csv(f"{inpath}/{field}_reference.csv")

    # clean files
    df_meta_clean, df_paa_clean, df_ref_clean = clean_data(df_meta, df_paa, df_ref)

    # match & keyword
    df_keyword_2016, df_control_2016 = get_keyword_subset(df_meta_clean, df_paa_clean, field, querry)

    # clean records 
    df_control_clean = clean_records(df_control_2016, "PaperId_control")
    df_experiment_clean = clean_records(df_keyword_2016, "PaperId_experiment")

    # get matches
    df_joined = get_matches(df_experiment_clean, df_control_clean)

    # check matching (for now does not subset)
    df_close_matches = check_matching(df_joined, df_control_clean)

    # to long format
    df_long_format = long_format(df_close_matches) 

    # get citing papers
    df_long_na, df_long_cited = get_citations(df_ref_clean, df_long_format)

    # citation delay
    df_outside_five, df_inside_five = citation_delay(df_meta_clean, df_long_cited, df_long_na)

    # days after 2010
    df_inside_five = days_after_2010(df_inside_five, datetime.date(2010, 1, 1))
    df_outside_five = days_after_2010(df_outside_five, datetime.date(2010, 1, 1))

    # clean columns
    df_ready = clean_columns(df_inside_five, df_outside_five)

    # write csv
    df_ready.to_csv(f"{outpath}/{field}_{querry}_matched.csv", index = False) 

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--inpath", required=True, type=str, help="path to folder with files")
    ap.add_argument("-f", "--field", required=True, type=str, help="field of study, e.g. psychology")
    ap.add_argument("-q", "--querry", required=True, type=str, help="querry to search for in titles, e.g. replicat")
    ap.add_argument("-o", "--outpath", required=True, type=str, help="path to folder for output csv")
    args = vars(ap.parse_args())

    main(inpath = args["inpath"], field = args["field"], querry = args["querry"], outpath = args["outpath"])
