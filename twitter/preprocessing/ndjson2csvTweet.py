"""
usage: 

where to type from: 
    '/work/50114/twitter' 

what to type: 
    python preprocessing/ndjson2csvTweet.py -i data/ndjson/tweet/ -o data/csv/tweet/

"""

import argparse
import os
import re
import pandas as pd
import ndjson
import datetime
from tqdm import tqdm
from pathlib import Path

def convert_to_df(data):
    """Converts a ndjson-file to a pd.DataFrame

    Args:
        data (.ndjson): .ndjson-file containing the necessary information

    Returns:
        pd.DataFrame: Dataframe containing the necessary information.
    """    

    dataframe = {
        "author_id": [row["author_id"] for row in data], 
        "conversation_id": [row["conversation_id"] for row in data], 
        "text": [row["text"] for row in data],
        "lang": [row["lang"] for row in data], 
        "created_at": [row["created_at"] for row in data], 
        # "hashtags": [", ".join([x["tag"] for x in row.get("entities").get("hashtags")]) if row.get("entities") and row.get("entities").get("hashtags") else None for row in data], # hmmm... I don't think I have this right now. 
        "retweet_count": [row["public_metrics"]["retweet_count"] for row in data], 
        "reply_count": [row["public_metrics"]["reply_count"] for row in data], 
        "like_count": [row["public_metrics"]["like_count"] for row in data],
        "retweet": [row["referenced_tweets"][0]["type"] if row.get("referenced_tweets") else "original" for row in data]
    }

    return pd.DataFrame(dataframe)

def load_data(inpath, outpath):
    """Loads all the ndjson-files in the specified data_path, converts them to a df and concatenates them.
    Args:
        data_path (str): Path to the folder of the ndjson-files.
    Returns:
        pd.DataFrame: Concatenated dataframe of all the files.
    """    
    
    # something with getting the filenames that we have done before. 
    dfs = []
    for filename in tqdm(Path(inpath).glob("*.ndjson")):
        # find good way of getting "openscience" for instance.  
        #base=os.path.splitext(os.path.basename(filename))[0]
        with open(filename, "r") as f: 
            data = ndjson.load(f)
        dfs.append(convert_to_df(data))

    main_df = pd.concat(dfs, axis = 0).reset_index(drop = True)
    main_df.to_csv(f"{outpath}openscience_tweet.csv", index=False)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-i','--inpath', required=True, help='path to dir with .ndjson input files')
    ap.add_argument('-o','--outpath', required=True, help='path to output directory for .csv file') 
    args = vars(ap.parse_args())

    df = load_data(inpath = args['inpath'], outpath = args['outpath'])