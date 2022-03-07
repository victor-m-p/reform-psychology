'''
VMP 2022-03-03: 
just used for sanity checking. 
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
        gathered_string = "None"
        
    return gathered_string 

# get mentions (referenced tweets)
def get_mentions_ref(row): 
    '''
    just to test what are in these two different ones
    '''
    try: 
        mentions_reference = row["referenced_tweets"][0]["entities"]["mentions"]
        has_reference = True
    except KeyError: 
        has_reference = False 

    if has_reference: 
        mentions_username = [x["username"] for x in mentions_reference]
        gathered_string = "|".join(mentions_username)
    else: 
        gathered_string = 'None'

    return gathered_string

# get mentions (entities)
def get_mentions_ent(row): 
    try: 
        mentions_entity = row["entities"]["mentions"]
        has_entity = True
    except KeyError: 
        has_entity = False 

    if has_entity: 
        mentions_username = [x["username"] for x in mentions_entity]
        gathered_string = "|".join(mentions_username)
    else: 
        gathered_string = 'None'

    return gathered_string

# check whether tweet has reference
def has_reference(row):
    '''
    True if 'referenced_tweets' = 'original' or 'replied_to' 
    False if 'referenced_tweets' = 'retweeted' or 'quoted' 
    '''
    try:
        row['referenced_tweets']
        has_reference = True
    except KeyError: 
        has_reference = False
        
    return has_reference

def create_dct(data): 
    '''
    data: <ndjson.loads> 
    ''' 
    lst = []
    for row in data: 
        if has_reference(row): 
            if row["referenced_tweets"][0]["type"] == "quoted":
                lst.append(row)
            else: 
                pass 
        else: 
            pass 

    return lst

def main(infile, outpath):
    print(f"--- loading file ---")
    data, filename_out = load_data(infile) 
    print(f"--- create dataframe ---")
    lst = create_dct(data)
    print(f"--- writing file ---")
    with open(f'{outpath}/{filename_out}_quote.pickle', 'wb') as handle:
        pickle.dump(lst, handle, protocol=pickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--infile", required=True, type=str, help="path to ndjson flattened file")
    ap.add_argument("-o", "--outpath", required=True, type=str, help="path to folder for output csv")
    args = vars(ap.parse_args())

    main(infile = args["infile"], outpath = args["outpath"])








