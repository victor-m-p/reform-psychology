'''
VMP 2022-03-03:
used to run sanity-checks on data. 
important document. 

'''

import pandas as pd
import numpy as np
import pickle 
pd.set_option('display.max_colwidth', None)

''' read pickle '''
with open("/work/50114/twitter/data/raw/preprocessed/bropenscience.pickle", "rb") as f:
    dct = pickle.load(f)

df = pd.DataFrame.from_dict(dct)

''' check distribution of different tweet types '''
def check_tweet_type(df):
    df_type = df.groupby('type_tweet').size().reset_index(name = 'count').sort_values('count', ascending=False)
    print("--- tweet types ---")
    print(df_type)

check_tweet_type(df)

''' check na/null across all columns (should be 0) '''
def check_na(df):
    '''
    should be all zeros 
    '''
    total_rows = len(df)
    df_na = df.isna().sum().sum()
    df_null = df.isnull().sum().sum()
    print(f"--- checking na/null ---")
    print(f"number rows: {total_rows}")
    print(f"number na: {df_na}")
    print(f"number null: {df_null}")

check_na(df)

''' check "None" in all columns '''
def check_none(df, type): 
    
    # get total rows first
    total_rows = len(df)

    # print 
    print(f"\n--- checking None for {type} ---")
    print(f"number rows: {total_rows}")

    # loop
    for i in df.columns:
        number_none = len(df[df[i] == "None"])
        if number_none > 0: 
            print(f"{i}: {number_none} / {round(number_none/total_rows*100, 2)}%")
        else:
            pass
        
# get sub-categories
df_rt = df[df["type_tweet"] == "retweeted"]
df_quote = df[df["type_tweet"] == "quoted"]
df_orig = df[df["type_tweet"] == "original"]
df_reply = df[df["type_tweet"] == "replied_to"]

# check none across tweet types (generally good): 
check_none(df, "overall") # always has main & most reference (not always location, mentions)
check_none(df_rt, "retweet") # always has reference (not always mentions)
check_none(df_quote, "quote") # always has reference (not always mentions)
check_none(df_orig, "original") # never has reference
check_none(df_reply, "reply") # always has reference (sometimes lacking author here)

''' check whether conv. id. match'''
def check_conv(df, type): 
    number_rows = len(df)
    potential_matches = len(df[(df["main_conv_id"] != "None") & (df["ref_conv_id"] != "None")])
    actual_matches = len(df[df['main_conv_id'] == df['ref_conv_id']])
    
    # print information
    print(f"\n--- check conv. id. ({type}) ---")
    print(f"number rows: {number_rows}")
    print(f"potential matches: {potential_matches} / {round(potential_matches/number_rows*100,2)}% of total")
    print(f"actual matches: {actual_matches} / {round(actual_matches/potential_matches*100, 2)}% of potential")
    
check_conv(df, "overall")
check_conv(df_rt, "retweet") # no retweets share conv. id. (does retweet become new conversation?)
check_conv(df_quote, "quote") # < 1% share conv. id. (does quote become new conversation?)
check_conv(df_reply, "reply") # 100% share conv. id. (this is the purpose)

