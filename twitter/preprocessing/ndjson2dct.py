'''
VMP 2022-03-03: key document
converts ndjson to dictionary and saves pickle.
retreives all the key information that we need for analysis. 

change-log: 
2022-04-03: changed "None" to None. 
'''

import pandas as pd 
from tqdm import tqdm
import os
import argparse 
import ndjson
import json
from pathlib import Path
import re
import pickle

# load data
def load_data(infile):

    with open(infile, "r") as f: 
        data = ndjson.load(f)

    filename_out = re.search("twarc_flat/(.*).ndjson", infile)[1]

    return data, filename_out

# get mentions information (probably going to get outdated). 
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

    if has_entity and has_reference: # implicit True
        mentions_id_reference = [x[id_term] for x in mentions_reference]
        mentions_id_entity = [x[id_term] for x in mentions_entity]
        gathered_lst = list(set(mentions_id_entity + mentions_id_reference))
        gathered_string = "|".join(gathered_lst)
    
    elif has_entity and has_reference == False: 
        mentions_id_entity = [x[id_term] for x in mentions_entity]
        gathered_string = "|".join(mentions_id_entity)

    elif has_entity == False and has_reference: 
        mentions_id_reference = [x[id_term] for x in mentions_reference]
        gathered_string = "|".join(mentions_id_reference)

    else: 
        gathered_string = None
        
    return gathered_string 

# get mentions (referenced tweets)
# overlaps a bit with has_attribute (could perhaps make smarter)
def get_mentions_ref(row, id_term): 
    '''
    just to test what are in these two different ones
    '''
    try: 
        mentions_reference = row["referenced_tweets"][0]["entities"]["mentions"]
        has_reference = True
    except KeyError: 
        has_reference = False 

    if has_reference: 
        mentions_username = [x[id_term] for x in mentions_reference]
        gathered_string = "|".join(mentions_username)
    else: 
        gathered_string = None

    return gathered_string

# get mentions (entities)
# overlaps a bit with has_attribute (could perhaps make smarter)
def get_mentions_ent(row, id_term): 
    try: 
        mentions_entity = row["entities"]["mentions"]
        has_entity = True
    except KeyError: 
        has_entity = False 

    if has_entity: 
        mentions_username = [x[id_term] for x in mentions_entity]
        gathered_string = "|".join(mentions_username)
    else: 
        gathered_string = None

    return gathered_string

## could be made smoother with regards to handling of diffferent number of args.
def has_attribute(row, *args): 

    if len(args) == 1: 
        try: 
            row[args[0]]
            has_attribute = True
        except KeyError: 
            has_attribute = False
        
    if len(args) == 2: 
        try: 
            row[args[0]][args[1]]
            has_attribute = True
        except KeyError: 
            has_attribute = False
    
    if len(args) == 3: 
        try: 
            row[args[0]][args[1]][args[2]]
            has_attribute = True
        except KeyError: 
            has_attribute = False
    
    if len(args) == 4: 
        try: 
            row[args[0]][args[1]][args[2]][args[3]]
            has_attribute = True
        except KeyError: 
            has_attribute = False
    
    return has_attribute 

def create_dct(data): 
    '''
    data: <ndjson.loads> 
    ''' 
    dct = {
        # type of tweet
        'type_tweet': [row["referenced_tweets"][0]["type"] if has_attribute(row, "referenced_tweets", 0, "type") else "original" for row in data],

        # information for main tweet
        'main_tweet_id': [row["id"] for row in data],
        'main_conv_id': [row["conversation_id"] for row in data],
        'main_author_id': [row["author_id"] for row in data],
        'main_author_name': [row['author']['name'] for row in data],
        'main_author_username': [row['author']['username'] for row in data],
        'main_text': [row["text"] for row in data],
        'main_description': [row["author"]["description"] for row in data],
        'main_lang': [row["lang"] for row in data],
        'main_location': [row["author"]["location"] if has_attribute(row, "author", "location") else None for row in data],
        'main_countrycode': [row["geo"]["country_code"] if has_attribute(row, "geo", "country_code") else None for row in data],
        'main_tweet_date': [row['created_at'] for row in data],
        'main_account_date': [row["author"]["created_at"] for row in data],
        'main_mentions_username': [get_mentions_ent(row, "username") for row in data],
        'main_mentions_author_id': [get_mentions_ent(row, "id") for row in data],

        # id for reference: 
        'ref_tweet_id': [row["referenced_tweets"][0]["id"] if has_attribute(row, "referenced_tweets", 0, "id") else None for row in data],
        'ref_conv_id': [row["referenced_tweets"][0]["conversation_id"] if has_attribute(row, "referenced_tweets", 0, "conversation_id") else None for row in data],
        'ref_author_id': [row["referenced_tweets"][0]["author_id"] if has_attribute(row, "referenced_tweets", 0, "author_id") else None for row in data],
        'ref_author_name': [row["referenced_tweets"][0]["author"]["name"] if has_attribute(row, "referenced_tweets", 0, "author", "name") else None for row in data],
        'ref_author_username': [row["referenced_tweets"][0]["author"]["username"] if has_attribute(row, "referenced_tweets", 0, "author", "username") else None for row in data], 
        'ref_text': [row["referenced_tweets"][0]["text"] if has_attribute(row, "referenced_tweets", 0, "text") else None for row in data],
        'ref_description': [row["referenced_tweets"][0]["author"]["description"] if has_attribute(row, "referenced_tweets", 0, "author", "description") else None for row in data],
        'ref_lang': [row["referenced_tweets"][0]["lang"] if has_attribute(row, "referenced_tweets", 0, "lang") else None for row in data],
        'ref_location': [row["referenced_tweets"][0]["author"]["location"] if has_attribute(row, "referenced_tweets", 0, "author", "location") else None for row in data],
        'ref_countrycode': [row["referenced_tweets"][0]["geo"]["country_code"] if has_attribute(row, "referenced_tweets", 0, "geo", "country_code") else None for row in data],
        'ref_tweet_date': [row["referenced_tweets"][0]["created_at"] if has_attribute(row, "referenced_tweets", 0, "created_at") else None for row in data],
        'ref_account_date': [row["referenced_tweets"][0]["author"]["created_at"] if has_attribute(row, "referenced_tweets", 0, "author", "created_at") else None for row in data],
        'ref_mentions_username': [get_mentions_ref(row, "username") for row in data],
        'ref_mentions_author_id': [get_mentions_ref(row, "id") for row in data],

        # id for reply: (not sure whether I need this)
        'reply_author_id': [row["in_reply_to_user_id"] if has_attribute(row, "in_reply_to_user_id") else None for row in data],

        # mentions total: (probably not needed)
        'mentions_total_username': [get_mentions_id(row, "username") for row in data],
        'mentions_total_author_id': [get_mentions_id(row, "id") for row in data],

        # public metrics (can get for reference as well)
        'tweet_retweet_count': [row['public_metrics']['retweet_count'] for row in data],
        'tweet_reply_count': [row['public_metrics']['reply_count'] for row in data],
        'tweet_like_count': [row['public_metrics']['like_count'] for row in data],
        'tweet_quote_count': [row['public_metrics']['quote_count'] for row in data],
        'author_followers_count': [row["author"]["public_metrics"]["followers_count"] for row in data],
        'author_following_count': [row["author"]["public_metrics"]["following_count"] for row in data],
        'author_tweet_count': [row["author"]["public_metrics"]["tweet_count"] for row in data],
        
        # other 
        'retrieved_at': [row["__twarc"]["retrieved_at"] for row in data]
    }

    return dct

def main(infile, outpath):
    print(f"--- loading file ---")
    data, filename_out = load_data(infile) 
    print(f"--- create dataframe ---")
    dct = create_dct(data)
    print(f"--- writing file ---")
    with open(f'{outpath}/{filename_out}.pickle', 'wb') as handle:
        pickle.dump(dct, handle, protocol=pickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--infile", required=True, type=str, help="path to ndjson flattened file")
    ap.add_argument("-o", "--outpath", required=True, type=str, help="path to folder for output csv")
    args = vars(ap.parse_args())

    main(infile = args["infile"], outpath = args["outpath"])








