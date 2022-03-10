'''
VMP 2022-03-07: 
right now we do stopword removal twice. 
not sure whether this is good practice, but it seems to work well
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
        self.clean_lemmas = [token for token in self.lemmatized.split() if token not in stopwords.words('english')]
        self.clean_lemmatized = ' '.join(self.clean_lemmas)
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
        text = re.sub(r"@[^\s]+", " ", text) # remove handles / mentions
        text = re.sub(r'[^\w\s]', "", text) # remove punctuation and emojis
        text = re.sub(r'\d+', ' ', text) # 
        text = re.sub(r'\W+', ' ', text) # 
        text = re.sub(r'\s+', ' ', text) # excess whitespace with single :) 

        return text    

# check stuff
infile = "/work/50114/twitter/data/raw/preprocessed/bropenscience.pickle"
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

# put some string-cols together to have something to test with 

test_string = ''
for i in range(10):
    test_string = test_string + ' ' + df_sub.iloc[i]["text"]

paper_instance = TextFeatures(test_string)

paper_instance.tokenized
paper_instance.lemmatized

# 




# new stop words 
more_words = ['im', 'ill']

# additional stopwords: 
additional_stopwords = ["im", "dont", "also", "one", "see", "ive", "well", "thats", "cant"]

nltk_stopwords = stopwords.words('english')
total_stopwords = nltk_stopwords + additional_stopwords 
total_stopwords