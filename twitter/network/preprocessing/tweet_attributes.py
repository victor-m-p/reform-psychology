'''
VMP 2022-03-03:
tweet-based information: 

# log 
* cols: username, time, type 
'''

# imports
import pandas as pd
import numpy as np
import pickle 
import re 
import argparse 
from pathlib import Path

# convert dates & get month
def convert_dates(df, cols): 
    '''
    df: <pd.dataframe> 
    cols: <list> list of column names to convert to datetime

    returns: 
    (1) converted column 
    '''

    for i in cols: 
        df[i] = df[i].astype('datetime64[ns]')
    return df

# main 
def main(infile, outpath): 
    print(f"--- running: tweet attributes ---")

    ## read data & get filename
    print(f"--> loading file")
    with open(f"{infile}", "rb") as f:
        dct = pickle.load(f)

    df = pd.DataFrame.from_dict(dct)
    outname = re.search("preprocessed/(.*).pickle", infile)[1]

    # subset columns & rename
    print(f"--> column organization") 
    columns = ["main_author_username", "main_tweet_date", "type_tweet"]
    df = df[columns]
    df = df.rename(columns={
        'main_author_username': 'username',
        'main_tweet_date': 'tweet_date',
        })

    ## dates
    print(f"--> converting dates")
    cols = ["tweet_date"]
    df = convert_dates(df, cols)

    ## write file 
    print(f"--> writing file")
    df.to_csv(f'{outpath}/{outname}_tweets.csv', index = False)  

    # print 
    print(f"--- finished: tweeet attributes ---")
    
if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--infile", required=True, type=str, help="path to input file (.pickle from ../../data/raw/preprocessed/file.pickle)")
    ap.add_argument("-o", "--outpath", required=True, type=str, help="path to folder for output csv (../../data/network/preprocessed)")
    args = vars(ap.parse_args())

    main(infile = args["infile"], outpath = args["outpath"])
