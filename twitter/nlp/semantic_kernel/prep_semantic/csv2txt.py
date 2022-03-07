'''
VMP 2022-03-07: converts .csv to .txt files (used)

usage, e.g.:  
python prep_semantic/csv2txt.py -i data/text_all.csv -o data/data_semantic/text_all

questions: 
# (1) should it be run on cleaned text or cleaned lemmas? 
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

def main(infile, outpath):
    df = pd.read_csv(f"{infile}")
    
    # loop over these and write out stuff in txt files
    for index, row in tqdm(df.iterrows()): 
        # get the values for each row. 
        ID = row["tweet_id"]
        clean_text = row["clean_text"] # not sure which one 
        clean_lemma = row["clean_lemma"] # not sure which one 

        # filename with id 
        filename = f'{ID}.txt'

        # save text file 
        with open(os.path.join(outpath, 'text', filename), "w") as f:
            f.write(clean_text)

        # save lemma file 
        with open(os.path.join(outpath, 'lemma', filename), "w") as f:
            f.write(clean_lemma)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--infile", required = True, type = str, help = "file to process (.csv)")
    ap.add_argument("-o", "--outpath", required = True, type = str, help = "path to output folder for cleaned text files (.txt)")
    args = vars(ap.parse_args())

    main(infile = args['infile'], outpath = args['outpath'])