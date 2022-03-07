'''
VMP 2022-03-06: 
plot author attributes over time

log: 
* make plot without unknown 
* annotate with lines / event detection 
* do it for unique authors & for only original tweets 
'''

# packages 
import pandas as pd 
import numpy as np
import re
import matplotlib.pyplot as plt 
import seaborn as sns 
from itertools import product 
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates

''' visual setup '''
from configuration import * 
ms, figsize, dpi, c_gender, c_bropenscience = plot_configuration()

# load data (csv)
author_file = "/work/50114/twitter/data/network/preprocessed/bropenscience_authors.csv"
tweet_file = "/work/50114/twitter/data/network/preprocessed/bropenscience_tweets.csv"
df_tweet = pd.read_csv(f"{tweet_file}", parse_dates = ['tweet_date'])
df_author = pd.read_csv(f"{author_file}", parse_dates = ['account_date'])

# get month
df_tweet['tweet_month'] = df_tweet["tweet_date"].dt.to_period('m')
df_author['account_month'] = df_author['account_date'].dt.to_period('m')

# merge author and tweet information (no data loss here)
def gather_tweets(df_author, df_tweets, merge_on): 
    '''
    df_author: <pd.dataframe> 
    df_tweets: <pd.dataframe>
    merge_on: <str> column name to merge on 
    '''
    
    # merge
    df_gathered = df_author.merge(df_tweets, on = merge_on, how = 'inner')

    # print information
    print(f"number of tweets before merge: {len(df_tweets)}")
    print(f"number of tweets after merge: {len(df_gathered)}")

    return df_gathered

df_gathered = gather_tweets(df_author, df_tweet, "username")

# get tweeter age: 
def tweeter_age(df, date_account, date_tweet): 
    '''
    df: <pd.dataframe> 
    date_account: <str> column for account created date
    date_tweet: <str> column for tweet date

    NB: does this by month (rather than exact date)
    '''

    df["tweeter_age_months"] = df[date_account].astype(int) - df[date_tweet].astype(int)
    return df

df_gathered = tweeter_age(df_gathered, "tweet_month", "account_month")

# all (counts authors multiple times)
## get data by month
def aggregate(df, time_col, agg_col):
    '''
    df: <pd.dataframe> 
    time_col: <str> time column (e.g. "tweet_month")
    agg_col: <str> aggregation column (e.g. "gender")
    '''
    
    # aggregate data
    df = df.groupby([time_col, agg_col]).size().reset_index(name = 'count')
    print(f"length df: {len(df)}")
    # if missing dates 
    earliest_month = df[time_col].min()
    last_month = df[time_col].max()

    # get date list filled
    month_list = []
    while earliest_month <= last_month: 
        month_list.append(earliest_month)
        earliest_month += 1
    
    # get all grouping var 
    all_grouping = df[agg_col].unique()

    # create grid dataframe (all comb. of both variables)
    df_grid = pd.DataFrame(list(product(month_list, all_grouping)), columns = [time_col, agg_col])
    print(f"length grid: {len(df_grid)}")
    # put it back in 
    df_grid = df_grid.convert_dtypes() # important for nan and type conversion
    df = df.convert_dtypes() # important for nan and type conversion
    df_clean = df_grid.merge(df, on = [time_col, agg_col], how = "left")
    df_clean["count"] = df_clean["count"].fillna(0) # fill na with 0 
    print(f"length clean: {len(df_clean)}")
    
    return df_clean

df_clean = aggregate(df_gathered, "tweet_month", "gender")

# plot frequency
def plot_frequency(df, x, y, hue, palette, query, outpath, figsize, dpi): 
    '''
    df: <pd.dataframe> 
    x: <str> x variable (time, e.g. "tweet_month")
    y: <str> y variable (summarized, e.g. "count")
    hue: <str> grouping/hue variable (e.g. "gender")
    '''

    # preparation of data + cumsum
    df["date"] = df[x].dt.to_timestamp('m')
    df[f'{y}_cumsum'] = df.groupby(hue)[y].cumsum()

    # setup
    fig, axes = plt.subplots(1, 2, figsize = figsize, dpi = dpi, constrained_layout=True)

    # plot 
    sns.lineplot(
        data = df, 
        x = "date", 
        y = y,
        hue = hue,
        palette = palette,
        ax = axes[0])

    sns.lineplot(
        data = df, 
        x = "date", 
        y = f"{y}_cumsum",
        hue = hue,
        palette = palette,
        ax = axes[1])

    # handling dates & fixing x label 
    date_form = DateFormatter("%Y-%m")
    for i in [0, 1]: 
        axes[i].xaxis.set_major_formatter(date_form)
        axes[i].xaxis.set_major_locator(mdates.YearLocator(1))
        axes[i].set_ylabel('count')
        axes[i].legend(frameon = False)

    # titles 
    axes[0].set_title('count')
    axes[1].set_title('count (cumsum)')
    plt.suptitle(f"{query} frequency")

    # save 
    plt.savefig(f"{outpath}/{query}_frequency.pdf")

# actually plot it 
plot_frequency(
    df = df_clean, 
    x = "tweet_month",
    y = "count",
    hue = "gender",
    palette = c_gender,
    query = "bropenscience",
    outpath = '/work/50114/twitter/fig/network/attributes',
    figsize = (11.69, 4),
    dpi = dpi
)
