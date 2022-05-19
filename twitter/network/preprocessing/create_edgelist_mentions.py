'''
VMP 2022-03-04: 
creating edgelist.
need a required (FALSE) in the add_arguments() 
this has not been develop to being done
'''

# imports 
import pandas as pd
import numpy as np
import pickle 
import re 
import argparse 
from pathlib import Path
pd.set_option('mode.chained_assignment', None) # suppresses and turn off the warning

''' convenience function '''
def get_weighted(df, cols): 
    '''
    df: <pd.dataframe> 
    cols: <list> list of column-names
    '''
    df = df.groupby(cols).size().reset_index(name = 'weight')
    return df 

## first concat them 
def gather_tweet_types(df_lst, group_cols, remove_self_reference = True):
    '''
    df_lst: <list> list of dataframes 
    group_cols: <list> list of column names to group by 
    remove_self: <bool> whether to remove self-links 
    '''
    
    df_main = pd.concat(df_lst)
    df_total = df_main.groupby(group_cols)['weight'].sum().reset_index(name = 'weight')
    df_total.sort_values('weight', ascending=False).head(5)
    if remove_self_reference: 
        df_total = df_total[df_total["username_from"] != df_total["username_to"]]
    return df_total

def main(infile, outpath, remove_self_reference = True): 
    print(f"--- creating edgelist ---")
    print(f"remove self-reference: {remove_self_reference}")
    ## read data & get filename
    with open(f"{infile}", "rb") as f:
        dct = pickle.load(f)

    df = pd.DataFrame.from_dict(dct)
    outname = re.search("preprocessed/(.*).pickle", infile)[1]

    ## subset columns & rename 
    subset_cols = ["main_author_username", "ref_author_username", "main_text", "type_tweet"]
    df = df[subset_cols]
    df = df.rename(columns = {
        'main_author_username': 'username_from',
        'ref_author_username': 'username_to'
    })

    # clean tweet types individually: 
    group_cols = ['username_from', 'username_to']

    ## (1) quoted --> original 
    ### (1.1) simple here: 
    df_quoted = df[df["type_tweet"] == "quoted"]
    df_quoted_weight = get_weighted(df_quoted, group_cols)

    ## (2) RT --> original 
    df_retweet = df[df["type_tweet"] == "retweeted"]
    df_retweet_weight = get_weighted(df_retweet, group_cols)

    ## # (3) reply --> original
    ## (3.1) this is the tricky case: you can reply to more than one other person. 
    df_reply = df[df["type_tweet"] == "replied_to"]

    ## (3.1.1) split them up by whether they reference or not 
    df_reply_ref = df_reply[~df_reply["username_to"].isnull()]
    df_reply_noref = df_reply[df_reply["username_to"].isnull()]

    ## (3.1.2) we can treat those that reference the same as the other tweets 
    df_reply_ref_weight = get_weighted(df_reply_ref, group_cols)

    ## (3.1.3) for those that do not reference we have to do some manual stuff
    #### find reply in text 
    reply_regex = "(@\w+) "
    df_reply_noref["username_to"] = ["|".join(re.findall(reply_regex, x)).replace('@', '') for x in df_reply_noref["main_text"]]
    #### explode 
    # https://medium.com/analytics-vidhya/pandas-explode-b162e7a85d3f
    df_reply_noref_explode = df_reply_noref.assign(username_to = df_reply_noref['username_to'].str.split('|')).explode('username_to')
    df_reply_noref_weight = get_weighted(df_reply_noref_explode, group_cols)

    # gather everything: 
    df_lst = [df_quoted_weight, df_retweet_weight, df_reply_ref_weight, df_reply_noref_weight]
    group_cols = ['username_from', 'username_to']
    df_clean = gather_tweet_types(df_lst, group_cols, remove_self_reference)

    # write output 
    filename = f"{outpath}{outname}_edgelist_simple.csv"
    colnames = list(df_clean.columns)
    print(f"writing file: {filename}")
    print(f"colnames: {colnames}")
    df_clean.to_csv(f"{filename}", index = False)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--infile", required=True, type=str, help="path to input file (.pickle from preprocessed)")
    ap.add_argument("-o", "--outpath", required=True, type=str, help="path to folder for output csv")
    ap.add_argument("-f", "--false", default=True, action="store_false", help="remove self-citations, default True") 
    args = vars(ap.parse_args())

    main(infile = args["infile"], outpath = args["outpath"], remove_self_reference = args["false"])
