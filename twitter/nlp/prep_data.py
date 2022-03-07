'''
2022-31-01: TAKEN FROM cn-some
usage, e.g. 
python prep_semantic/csv2txt.py -i dataframe_all_from/text_all.csv -o data_semantic/text_all
'''

# import stuff
import pandas as pd
import numpy as np
import re
from tqdm import tqdm
import os
import argparse 
from pathlib import Path
import io

# 
def main(inFile, outPath):
    df = pd.read_csv(f"{inFile}")
    
    # loop over these and write out stuff in txt files
    for index, row in tqdm(df.iterrows()): 
        if row["lang"] == "en": # only english 

            # get the values for each row. 
            ID = row["tweet_id"]
            clean_tmp = row["clean_text"]

            # save file 
            filename = f'{ID}.txt'
            with open(os.path.join(outPath, filename), "w") as text_file:
                text_file.write(clean_tmp)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--inFile", required=True, type=str, help="file to process (csv)")
    ap.add_argument("-o", "--outPath", required=True, type=str, help='path to folder for saving output files (txt)')
    args = vars(ap.parse_args())

    main(inFile = args['inFile'], outPath = args['outPath'])