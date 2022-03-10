'''
VMP 2022-03-03:
author-based information: 
gender (genderization),
account-created-at (twitter-age),
country (country-code)

NB: 
# (1) not using any nlp / matching yet (could look at description + text) 
# (2) not looking at "location" yet (would be some work) 
# (3) remember that we have more attributes (e.g. followers count)
'''

# packages
import pandas as pd
import numpy as np
import pickle 
import gender_guesser.detector as gender # https://pypi.org/project/gender-guesser/
import pycountry 
import re 
import argparse 
from pathlib import Path

''' create author-centered data '''
def create_subset(df, type): 
    '''
    df: <pd.dataframe> 
    type: <str> "main" or "ref"
    '''

    df_sub = df[[
        f"{type}_author_username", 
        f"{type}_author_name", 
        f"{type}_countrycode", 
        f"{type}_account_date"]]

    df_clean = df_sub.rename(columns = {
        f'{type}_author_username': 'username',
        f'{type}_author_name': 'name',
        f'{type}_countrycode': 'countrycode',
        f'{type}_account_date': 'account_date'
    })

    return df_clean 

''' fix countrycode '''
# get the newest that is non-na (otherwise use na)
def country_code_mode(df): 
    '''
    d: <pd.dataframe>: data with at least "username" and "countrycode" columns

    explanation: 
    most recent country if any non-na, otherwise na 
    '''

    # (1) subset those with non-nan 
    df_notna = df[~df["countrycode"].isnull()][["countrycode", "username"]]
    df_na = df.drop(columns='countrycode').drop_duplicates()

    # (2) ties extremely unlikely, so fine: 
    df_new = df_notna.groupby('username').sample(n = 1, random_state = 113)
    df_global = df_new.merge(df_na, on = 'username', how = 'outer')
    
    '''
    # get the mode of country
    df_countrycode = df.groupby('username')['countrycode'].apply(pd.Series.mode).reset_index()
    df_countrycode = df_countrycode[["username", "countrycode"]]
    df_countrycode = df_countrycode.sample(frac=1).drop_duplicates(subset='username').reset_index(drop=True)

    # merge back into original data
    df = df.rename(columns = {'countrycode': 'countrycode_original'})
    df_cleaned = df.merge(df_countrycode, on = 'username', how = 'left')
    df_cleaned = df_cleaned.drop(columns = ['countrycode_original'])
    df_cleaned = df_cleaned.drop_duplicates() 

    # print information 
    rows_total = len(df_cleaned)
    username_total = len(df_cleaned["username"].drop_duplicates())
    has_countrycode = len(df_cleaned[~df_cleaned["countrycode"].isnull()])
    print(f"* total rows: {rows_total}")
    print(f"* username total: {username_total}")
    print(f"* has countrycode: {has_countrycode}")

    # return df 
    return df_cleaned 
    '''
    return df_global 

''' convert dates '''
# conver_dates to datetime64[ns] 
def convert_dates(df, cols): 
    '''
    df: <pd.dataframe> 
    cols: <list> list of column names to convert to datetime
    '''

    for i in cols: 
        df[i] = df[i].astype('datetime64[ns]')
    return df

''' genderization '''
# doing it solely based on username right now, other options: 
# (a) include country (but we have so few) 
# (b) he/him, they/them, her/she thing from "description" 

# function to get first name 
def assign_one_name(regex, name):
    '''
    regex: <str> regex string 
    name: <str> name 

    returns: first name (before whitespace)
    ''' 
    try:  # isinstance(name, str) does not work because of NoneType (e.g. weird characters)
        first_name = re.match(regex, name)[0]
    except TypeError: 
        first_name = None 
    return first_name 

# run function (looks good)
def add_first_name(df, regex_firstname): 
    '''
    df: <pd.dataframe> with column "username" 
    regex_firstname: <str> regex for matching first name
    '''
    df["first_name"] = [assign_one_name(regex_firstname, x) for x in df["name"]]
    return df 

def assign_one_gender(first_name, d):
    '''
    first_name: <str> first name 
    d: <gender_guesser.detector.Detector> 
    ''' 
    if isinstance(first_name, str): 
        gender = d.get_gender(first_name)
    else: 
        gender = 'unknown'
    return gender 

def add_gender(df): 
    '''
    df: <pd.dataframe> 
    '''
    # get genders
    d = gender.Detector(case_sensitive=False)
    df["gender_raw"] = [assign_one_gender(x, d) for x in df["first_name"]]

    ## summarize different options ##
    conditions = [
        (df["gender_raw"] == 'male'),
        (df["gender_raw"] == "female"),
        (df["gender_raw"] == "unknown") | (df["gender_raw"] == "andy") | (df["gender_raw"] == "mostly_male") | (df["gender_raw"] == "mostly_female")
    ]
    choices = ["Male", "Female", "Unknown"]
    df["gender"] = np.select(conditions, choices, default = "error")
    
    # delete now obsolete columns
    # NB: could keep to document (can always go back here & do so) 
    df = df.drop(columns = ['gender_raw', 'first_name'])
    return df 

# main 
def main(infile, outpath): 
    # print 
    print(f"--- running: author attributes ---")

    ## read data & get filename
    print(f"--> loading file")
    with open(f"{infile}", "rb") as f:
        dct = pickle.load(f)

    print(f"--> creating dataframe")
    df = pd.DataFrame.from_dict(dct)
    outname = re.search("preprocessed/(.*).pickle", infile)[1]

    ## create subsets & concat
    print(f"--> creating subsets")
    df_main = create_subset(df, "main") 
    df_ref = create_subset(df, "ref")
    df = pd.concat([df_main, df_ref])
    
    ## country (takes a while bc. mode is slow)
    print(f"--> country codes")
    df = country_code_mode(df)

    ## dates
    print(f"--> account dates")
    cols = ["account_date"]
    df = convert_dates(df, cols)

    ## first name
    print(f"--> genderization")
    regex_firstname = r"(\w+)"
    df = add_first_name(df, regex_firstname)
    
    ## genderization
    df = add_gender(df) 

    ## write file 
    print(f"--> writing file")
    df.to_csv(f'{outpath}/{outname}_authors.csv', index = False)

    # print
    print(f"--- finished: author attributes")

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--infile", required=True, type=str, help="path to input file (.pickle from ../../data/raw/preprocessed/file.pickle)")
    ap.add_argument("-o", "--outpath", required=True, type=str, help="path to folder for output csv (../../data/network/preprocessed)")
    args = vars(ap.parse_args())

    main(infile = args["infile"], outpath = args["outpath"])
