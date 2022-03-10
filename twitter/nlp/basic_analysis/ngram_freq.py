'''
VMP 2022-03-07:
test bigrams
'''

import pandas as pd 
import itertools 
from collections import Counter
import re
from nltk import bigrams
import seaborn as sns 
pd.set_option('display.max_colwidth', None)

# load data
d = pd.read_csv("/work/50114/twitter/data/nlp/by_tweet/bropenscience_tweet_text.csv")

''' preparation '''
# test get-type by e.g. year: 
def get_dates(d): 
    '''
    d: <pd.dataframe> 
    '''
    d['tweet_date'] = d['tweet_date'].astype('datetime64[ns]')
    d['tweet_month'] = d["tweet_date"].dt.to_period('m')
    d['tweet_year'] = d['tweet_date'].dt.to_period('y')

    return d

d = get_dates(d)

''' unigrams '''
# unigrams
def get_top(d, type = "clean_lemma", n = None): 
    '''
    d: <pd.dataframe> 
    type: <str> column name (default: "clean_lemma")
    n: <int> top n (defeault: None which gets all)
    '''
    
    # basic processing 
    top_unigrams = d[type].str.split(expand=True).stack().value_counts().reset_index(name='count').rename(columns = {'index': 'word'})
    top_unigrams["total"] = top_unigrams["count"].sum()
    top_unigrams = top_unigrams.assign(fraction = lambda x: x["count"]/x["total"])
    top_unigrams = top_unigrams.sort_values('count', ascending = False)
    
    # subset if n defined 
    if n: 
        top_unigrams = top_unigrams.head(n)
    
    return top_unigrams

# def plot it 
def plot_top_n(d, type, n, selection = None): 
    '''
    d: <pd.dataframe> 
    type: <str> query, e.g. "bropenscience" 
    n: <int> how many words to plot 
    selection: <list> curated list to plot: defaults to none 
    '''
    
# plot over time: 
def plot_top_time(d, type, n, selection = None): 
    '''
    d: <pd.dataframe> 
    type: <str> query, e.g. "bropenscience" 
    n: <int> how many words to plot 
    selection: <list> curated list to plot: defaults to none 
    '''

def unigrams_over_time(d, period, type = "clean_lemma", n = None):
    '''
    d: <pd.dataframe> 
    period: <str> column name, e.g. "tweet_year" or "tweet_month" 
    type: <str> column name, e.g. "clean_lemma". 
    n: <int> how many to get per period 
    ''' 

    d_lst = []
    for i in sorted(d[period].unique()): 
        d_tmp = d[d[period] == i]
        d_tmp = get_top(d_tmp, type, n)
        d_tmp[period] = i 
        d_lst.append(d_tmp)
    d_concat = pd.concat(d_lst)
    return d_concat


d_year = unigrams_over_time(d, "tweet_year", n = 10)

# try to plot this # 
d_year["tweet_year"] = d_year["tweet_year"].dt.to_timestamp('y')
d_year = d_year.reset_index() # should be done earlier 

sns.lineplot(
        data = d_year, 
        x = "tweet_year", 
        y = "fraction",
        hue = "word")


''' bigrams '''
# remove stop words
terms_bigram = []
for tweet in d['clean_lemma']:
    # print(tweet, type(tweet))
    tokens = tweet.split()
    terms_bigram.append(list(bigrams(tokens)))

# count it 
bigrms = list(itertools.chain(*terms_bigram))

# Create counter of words in clean bigrams
bigram_counts = Counter(bigrms)
bigram_df = pd.DataFrame(bigram_counts.most_common(30), columns=["bigram", "count"])

bigram_df.head(5)



