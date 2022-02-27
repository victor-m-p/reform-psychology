"""
usage: mm

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
import pickle
from tqdm import tqdm
from pathlib import Path

def get_mentions(text): 
    '''
    input: <str> text of tweet 
    output: <str> all unique mentions separated by | 
    '''
    mentions = "|".join(list(dict.fromkeys(re.findall(r"(?<![@\w])@(\w{1,25})", text))))
    return mentions 

def get_type(tweet_data):
    '''
    True if 'referenced_tweets' = 'original' or 'replied_to' 
    False if 'referenced_tweets' = 'retweeted' or 'quoted' 
    '''
    if tweet_data.get('referenced_tweets'): 
        type = tweet_data["referenced_tweets"][0]["type"]
        if type == "retweeted" or type == "quoted": 
            return False 
        else: 
            return True
    else: 
        return True 

def convert_to_df(data):
    """Converts a ndjson-file to a pd.DataFrame

    Args:
        data (.ndjson): .ndjson-file containing the necessary information

    Returns:
        pd.DataFrame: Dataframe containing the necessary information.
    """    

    dataframe = {
        "tweet_id": [row["id"] for row in data], # tweet id 
        "author_id": [row["author_id"] for row in data], # binds with the other frame 
        #"conversation_id": [row["conversation_id"] for row in data], # not actually sure whether this is useful 
        #"text": [row["text"] if get_type(row) else "" for row in data], # this is sufficient. 
        #"lang": [row["lang"] for row in data], # probably nice before the textual analysis 
        "created_at": [row["created_at"] for row in data], # probably nice for analysis through time. 
        # "hashtags": [", ".join([x["tag"] for x in row.get("entities").get("hashtags")]) if row.get("entities") and row.get("entities").get("hashtags") else None for row in data], # hmmm... I don't think I have this right now. 
        # "retweet_count": [row["public_metrics"]["retweet_count"] for row in data], 
        # "reply_count": [row["public_metrics"]["reply_count"] for row in data], 
        # "like_count": [row["public_metrics"]["like_count"] for row in data],
        "tweet_type": [row["referenced_tweets"][0]["type"] if row.get("referenced_tweets") else "original" for row in data], # definitely want this 
        "tweet_id_original": [row["referenced_tweets"][0]["id"] if row.get("referenced_tweets") else row["id"] for row in data],
        "in_reply_to": [row["in_reply_to_user_id"] if row.get("in_reply_to_user_id") else "not_reply" for row in data],
        "mentionees": [get_mentions(row["text"]) if get_type(row) else "" for row in data] # only give mentions for original stuff. 
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
    main_df.to_csv(f"{outpath}openscience_tweet.csv", index=False, encoding='utf-8')
    # new try 
    #with open(f"{outpath}openscience_tweet.pkl", "wb") as f: 
    #    pickle.dump(main_df, f)

    # one try 
    #main_df.to_pickle(f"{outpath}openscience_tweet.pkl")

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-i','--inpath', required=True, help='path to dir with .ndjson input files')
    ap.add_argument('-o','--outpath', required=True, help='path to output directory for .csv file') 
    args = vars(ap.parse_args())

    load_data(inpath = args['inpath'], outpath = args['outpath'])