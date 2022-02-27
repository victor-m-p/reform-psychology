'''
checks ndjson from twarc
main cleaning document
needs to be moved
'''

import pandas as pd 
from tqdm import tqdm
import os
import argparse 
import ndjson
import json
from pathlib import Path
import re

# load data
def load_data(infile):

    with open(infile, "r") as f: 
        data = ndjson.load(f)

    filename_out = re.search("twarc_flat/(.*).ndjson", infile)[1]

    return data, filename_out

# get mentions information
def get_mentions_id(row, id_term):
    '''
    row: row of ndjson flattened twarc object
    id_term: <str> either "username", "name" or "id"  
    '''
    try: 
        mentions_reference = row["referenced_tweets"][0]["entities"]["mentions"]
        has_reference = True
    except KeyError: 
        has_reference = False
    
    try: 
        mentions_entity = row["entities"]["mentions"]
        has_entity = True
    except KeyError: 
        has_entity = False 

    if has_entity == True and has_reference == True:
        mentions_id_reference = [x[id_term] for x in mentions_reference]
        mentions_id_entity = [x[id_term] for x in mentions_entity]
        gathered_lst = list(set(mentions_id_entity + mentions_id_reference))
        gathered_string = "|".join(gathered_lst)
    
    elif has_entity == True and has_reference == False: 
        mentions_id_entity = [x[id_term] for x in mentions_entity]
        gathered_string = "|".join(mentions_id_entity)

    elif has_entity == False and has_reference == True: 
        mentions_id_reference = [x[id_term] for x in mentions_reference]
        gathered_string = "|".join(mentions_id_reference)

    else: 
        gathered_string = ""
        
    return gathered_string 

# check whether tweet has reference
def has_reference(row):
    '''
    True if 'referenced_tweets' = 'original' or 'replied_to' 
    False if 'referenced_tweets' = 'retweeted' or 'quoted' 
    '''
    try:
        ref_tweets = row['referenced_tweets']
        has_reference = True
    except KeyError: 
        has_reference = False
        
    return has_reference

def create_df(data): 
    '''
    data: <ndjson.loads> 
    ''' 
    df = pd.DataFrame({
        # raw text 
        'raw_text': [row["text"] for row in data],
        # id columns
        'tweet_id': [row["id"] for row in data],
        'author_id': [row["author_id"] for row in data],
        'reference_tweet_id': [row["referenced_tweets"][0]["id"] if has_reference(row) else "original" for row in data], # is this the one they RT or the original tweet?
        'conversation_id': [row["conversation_id"] for row in data],
        'author_name': [row['author']['name'] for row in data],
        'author_username': [row['author']['username'] for row in data],
        'in_reply_to_user_id': [row["in_reply_to_user_id"] if row.get("in_reply_to_user_id") else "not_reply" for row in data],
        # mentions id 
        'mentions_username': [get_mentions_id(row, "username") for row in data],
        ### 'mentions_name': [get_mentions_id(row, "name") for row in data],
        'mentions_id': [get_mentions_id(row, "id") for row in data],
        # public metrics
        'retweet_count': [row['public_metrics']['retweet_count'] for row in data],
        'reply_count': [row['public_metrics']['reply_count'] for row in data],
        'like_count': [row['public_metrics']['like_count'] for row in data],
        'quote_count': [row['public_metrics']['quote_count'] for row in data],
        'type_tweet': [row["referenced_tweets"][0]["type"] if has_reference(row) else "original" for row in data], # for row in data],
        'followers_count': [row["author"]["public_metrics"]["followers_count"] for row in data],
        'following_count': [row["author"]["public_metrics"]["following_count"] for row in data],
        'tweet_count': [row["author"]["public_metrics"]["tweet_count"] for row in data],
        # other 
        'lang': [row["lang"] for row in data],
        'description': [row["author"]["description"] for row in data],
        'tweet_created_at': [row['created_at'] for row in data],
        'account_created_at': [row["author"]["created_at"] for row in data],
        'retrieved_at': [row["__twarc"]["retrieved_at"] for row in data],
    })

    return df 

def main(infile, outpath):
    print(f"--- loading file ---")
    data, filename_out = load_data(infile) 
    print(f"--- create dataframe ---")
    df = create_df(data)
    print(f"--- writing file ---")
    df.to_csv(f"{outpath}/{filename_out}.csv", index = False)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--infile", required=True, type=str, help="path to ndjson flattened file")
    ap.add_argument("-o", "--outpath", required=True, type=str, help="path to folder for output csv")
    args = vars(ap.parse_args())

    main(infile = args["infile"], outpath = args["outpath"])








