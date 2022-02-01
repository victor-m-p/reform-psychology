'''
VMP 2022-01-31
# basic preprocessing 
# post id, author id, text, time. 
# not for "tweet_type" == ["retweeted", "quoted"]
# only for "lang" == "en" 
'''

# import stuff

import ndjson
import json
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
#from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
#from pdfminer.pdfpage import PDFPage
#from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
#from pdfminer.layout import LAParams
#import io

# from somewhere

class TextFeatures:
    """ Class for extracting lexical features from text  
    Input:
        text: str variable
    """
    def __init__(self, text):
        assert isinstance(text, str), "'text' must have type str."
        self.text = text
        self.cleaned_text = TextFeatures.normalizing_text(self.text)
        self.tokens = [token for token in self.cleaned_text.split() if token not in stopwords.words('english')] #without stopwords
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
        text = re.sub(r"(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov)\b/?(?!@)))", " ", text)
        text = re.sub(r"_", " ", text) #replace underscore with space
        text = re.sub(r'[^\w\s]', "", text) #remove punctuation and emojis
        text = re.sub(r'\d+', ' ', text)
        text = re.sub(r'\W+', ' ', text)
        text = re.sub(r'\s+', ' ', text) # excess whitespace with single :) 
        
        ### things to try 
        #text = re.sub('RT|Ms', ' ', text)
        #text = re.sub("@[A-Za-z0-9:]+", " ", text)
        #text = re.sub(r'http\S+', ' ', text)

        return text    

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

    column_names = ['tweet_id', 'author_id', 'clean_text', 'raw_text', 'created_at', 'lang']
    df = pd.DataFrame(columns = column_names)

    for row in data: 
        if get_type(row): #and row["lang"] == "en": 
            
            # clean text 
            raw_text = row["text"]

            try: 
                paper_instance = TextFeatures(raw_text)
                cleaned_text = paper_instance.cleaned_text
            except (AssertionError, AttributeError) as e: 
                cleaned_text = ''

            # put into dct
            df_tmp = pd.DataFrame({
                'tweet_id': [row["id"]], 
                'author_id': [row["author_id"]],
                'clean_text': [cleaned_text],
                'raw_text': [raw_text],
                'created_at': [row["created_at"]],
                'lang': [row["lang"]]
                })

            #print(df_tmp.head())
            df = df.append(df_tmp, ignore_index=True)

        else: 
            pass 

    return df 

# main
def main(inpath, outpath):

    # empty list
    dfs = []
    for filename in tqdm(Path(inpath).glob("*.ndjson")):
        # get all the data
        with open(filename, "r") as f: 
            data = ndjson.load(f)
        dfs.append(convert_to_df(data))

    main_df = pd.concat(dfs, axis = 0).reset_index(drop = True)
    main_df.to_csv(f"{outpath}NLP2CSV.csv", index=False, encoding='utf-8')

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--inpath", required=True, type=str, help="path to folder with input files")
    ap.add_argument("-o", "--outpath", required=True, type=str, help='path to folder for output csv')
    args = vars(ap.parse_args())

    main(inpath = args['inpath'], outpath = args['outpath'])