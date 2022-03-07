'''
VMP 2022-03-07
# basic preprocessing 

NB: 
# not for retweet (only original, reply, quote)
# post id, author id, text, time. 
# only for "lang" == "en" 

NB: 
# (1) uses some (modified) cleaning from CHCAA
# (2) can become an issue with .csv for tweet_id (we want string ideally) -- for now no issues detected
'''

# imports 
import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
import spacy
nlp = spacy.load("en_core_web_sm")
from tqdm import tqdm
import os
import argparse 
from pathlib import Path
import pickle
from tqdm import tqdm 

# modified version of CHCAA (some project) cleaning
class TextFeatures:
    """ Class for extracting lexical features from text  
    Input:
        text: str variable
    """
    def __init__(self, text):
        assert isinstance(text, str), "'text' must have type str."
        self.text = text
        self.cleaned_text = TextFeatures.normalizing_text(self.text)
        self.tokens = [token for token in self.cleaned_text.split() if token not in stopwords.words('english')] # without stopwords
        self.tokenized = nlp(' '.join(self.tokens))
        self.lemmas = [token.lemma_ for token in self.tokenized]
        self.lemmatized = ' '.join(self.lemmas)
        self.n_tokens = len(self.tokens)    
    
    @staticmethod
    def normalizing_text(text):
        #normalising (make lower, remove punctuation, fix abbreviations, etc.)
        cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
        text = re.sub(cleanr, ' ', text)
        text = text.lower() #lower case
        text = re.sub(r'http\S+', ' ', text) # removes everything after http
        text = re.sub(r"/", " ", text) # replace slash with space
        text = re.sub(r"_", " ", text) # replace underscore with space
        text = re.sub(r"@[A-Za-z0-9:]+", " ", text) # remove handles / mentions
        text = re.sub(r'[^\w\s]', "", text) # remove punctuation and emojis
        text = re.sub(r'\d+', ' ', text) # 
        text = re.sub(r'\W+', ' ', text) # 
        text = re.sub(r'\s+', ' ', text) # excess whitespace with single :) 

        return text    

def clean_text(data, TextFeatures):
    """Converts a ndjson-file to a pd.DataFrame

    Args:
        data (.ndjson): .ndjson-file containing the necessary information

    Returns:
        pd.DataFrame: Dataframe containing the necessary information.
    """    

    column_names = ['tweet_id', 'username', 'clean_text', 'raw_text', 'tweet_date']
    df_main = pd.DataFrame(columns = column_names)

    for index, row in tqdm(data.iterrows()): 

        # clean text 
        raw_text = row["text"]
        if isinstance(raw_text, str): 
            paper_instance = TextFeatures(raw_text)
            clean_text = paper_instance.cleaned_text
            clean_lemma = paper_instance.lemmatized 
        else: 
            clean_text = ''
            clean_lemma = ''

        # put into df
        df_tmp = pd.DataFrame({
            'tweet_id': [row["tweet_id"]], 
            'username': [row["username"]],
            'clean_text': [clean_text],
            'clean_lemma': [clean_lemma],
            'raw_text': [raw_text],
            'tweet_date': [row["tweet_date"]]
            })

        #print(df_tmp.head())
        df_main = df_main.append(df_tmp, ignore_index=True)
    
    #df_concat = pd.concat(df, axis = 0).reset_index(drop = True)

    return df_main

# main
def main(infile, outpath):
    # print information
    print(f"--- starting: cleaning tweets ---")

    # read data & get filename
    with open(f"{infile}", "rb") as f:
        dct = pickle.load(f)

    df = pd.DataFrame.from_dict(dct)
    outname = re.search("preprocessed/(.*).pickle", infile)[1]

    # only original tweets & lang = en
    df_orig = df[df["type_tweet"] != "retweeted"]
    df_orig = df_orig[df_orig["main_lang"] == "en"]

    # subset columns & rename
    cols = ["main_tweet_id", "main_author_username", "main_text", "main_tweet_date"]
    df_sub = df_orig[cols]
    df_sub = df_sub.rename(columns = {
        'main_tweet_id': 'tweet_id',
        'main_author_username': 'username',
        'main_text': 'text',
        'main_tweet_date': 'tweet_date'
        })

    # clean text data
    df_concat = clean_text(df_sub, TextFeatures)

    # print information
    print(f"length original (en) tweets: {len(df_sub)}")
    print(f"length cleaned tweets: {len(df_concat)}")

    # write file 
    df_concat.to_csv(f"{outpath}{outname}_tweet_text.csv", index=False)

    # print information
    print(f"--- finished: writing file ---")

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--infile", required=True, type=str, help="path to input file (pickle)")
    ap.add_argument("-o", "--outpath", required=True, type=str, help="path to folder for output csv")
    args = vars(ap.parse_args())

    main(infile = args['infile'], outpath = args['outpath'])