"""
usage: 

where to type from: 
    '/work/50114/twitter' 

what to type: 
    python preprocessing/ndjson2csvUser.py -i data/ndjson/user/ -o data/csv/user 

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
        "username": [row["username"] for row in data],
        "author_id": [row["id"] for row in data], # added.
        "followers_count": [row["public_metrics"]["followers_count"] for row in data], 
        "following_count": [row["public_metrics"]["following_count"] for row in data], 
        "tweet_count": [row["public_metrics"]["following_count"] for row in data],
        #"listed_count": [row["public_metrics"]["listed_count"] for row in data]
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
    main_df.to_csv(f"{outpath}openscience_user.csv", index=False, encoding='utf-8')
    #main_df.to_pickle(f"{outpath}openscience_user.pkl")

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-i','--inpath', required=True, help='path to dir with .ndjson input files')
    ap.add_argument('-o','--outpath', required=True, help='path to output directory for .csv file') 
    args = vars(ap.parse_args())

    load_data(inpath = args['inpath'], outpath = args['outpath'])
