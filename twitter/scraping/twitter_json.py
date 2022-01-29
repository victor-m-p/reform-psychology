'''
2021-29-01:
heavily inspired by the code (link).
run from bash script. 

'''
# https://towardsdatascience.com/an-extensive-guide-to-collecting-tweets-from-twitter-api-v2-for-academic-research-using-python-3-518fcb71df2a
import requests
import os
import json
import pandas as pd
import csv
import datetime
import dateutil.parser
import unicodedata
import time
import re 
import ndjson 
import argparse

# create headers
def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers

# create url 
def create_url(querry, start_date, end_date, max_results = 10):
    
    search_url = "https://api.twitter.com/2/tweets/search/all" #Change to the endpoint you want to collect data from

    #change params based on the endpoint you are using
    query_params = {'query': querry,
                    'start_time': start_date,
                    'end_time': end_date,
                    'max_results': max_results,
                    'expansions': 'author_id,in_reply_to_user_id,geo.place_id',
                    'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source',
                    'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
                    'place.fields': 'full_name,id,country,country_code,geo,name,place_type',
                    'next_token': {}}
    return (search_url, query_params)

def connect_to_endpoint(url, headers, params, next_token = None):
    params['next_token'] = next_token   #params object received from create_url function
    response = requests.request("GET", url, headers = headers, params = params)
    print("Endpoint Response Code: " + str(response.status_code))
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

''' specifics '''
#Inputs for tweets
#bearer_token = auth()
#headers = create_headers(bearer_token)
'''
# variables set from command line 
#querry = '"replicability" OR "reproducibility"'
querry = '"open science" OR "openscience"'
querryname = 'openscience' # cannot give the actual one 
outpath_tweet = "/work/50114/twitter/data/ndjson/tweet/" # outpath 
outpath_user = "/work/50114/twitter/data/ndjson/user/" # outpath
max_results = 50 # this is PER collection I think. 

# variables we need to have somewhere else in some list - not sure how we do this well.
querry = '"open science" OR "openscience"'
'''

def get_tweets(start_dates, end_dates, max_results, max_count, querry, querryname, outpath_tweet, outpath_user, bearer_token):
    '''
    start_dates: <list> in format: ['2021-01-01T00:00:00.000Z', ...]
    end_dates: <list> in format: ['2021-01-31T00:00:00.000Z', ...]
    max_results: <int> max results PER querry (is my understanding). 
    max_count: <int> max results per date interval. 
    querry: <string> querry string, e.g. '"open science" OR "openscience"' 
    querryname: <string> matching querry string, e.g. "openscience" 
    outpath_tweet: <string> outpath for .ndjson main data. 
    outpath_user: <string> outpath for .ndjson user data.
    bearer_token: <string> twitter bearer token.
    '''
    
    # authentication
    headers = create_headers(bearer_token)

    # setup
    total_tweets = 0
    reg_pattern = r"\d{4}-\d{2}-\d{2}" 

    # start loop 
    for i in range(0,len(start_dates)):

        # File name 
        json_name = re.match(reg_pattern, start_dates[i])[0]
        querryname = querryname
        name_counter = 0

        # Inputs
        count = 0 # Counting tweets per time period
        max_count = 100 # Max tweets per time period
        flag = True
        next_token = None
        
        # Check if flag is true
        while flag:
            name_counter += 1 
            # Check if max_count reached
            if count >= max_count:
                break
            print("-------------------")
            print("Token: ", next_token)
            url = create_url(querry, start_dates[i],end_dates[i], max_results)
            json_response = connect_to_endpoint(url[0], headers, url[1], next_token)
            result_count = json_response['meta']['result_count'] # 

            if 'next_token' in json_response['meta']:
                # Save the token to use for next call
                next_token = json_response['meta']['next_token']
                print("Next Token: ", next_token)
                if result_count is not None and result_count > 0 and next_token is not None:
                    print("Start Date: ", start_dates[i])


                    # could turn into function I guess    
                    tweet_info = json_response.get("data")
                    user_info = json_response.get("includes").get("users")
                    
                    with open(f'{outpath_tweet}{json_name}_{querryname}_{name_counter}_tweet.ndjson', 'w') as f:
                        ndjson.dump(tweet_info, f)

                    with open(f'{outpath_user}{json_name}_{querryname}_{name_counter}_user.ndjson', 'w') as f:
                        ndjson.dump(user_info, f)

                    count += result_count
                    total_tweets += result_count
                    print("Total # of Tweets added: ", total_tweets) 
                    print("-------------------")
                    time.sleep(5)             
            # If no next token exists
            else:
                if result_count is not None and result_count > 0:
                    print("-------------------")
                    print("Start Date: ", start_dates[i])


                    # could turn into function I guess    
                    tweet_info = json_response.get("data")
                    user_info = json_response.get("includes").get("users")
                    
                    with open(f'{outpath_tweet}{json_name}_{querryname}_{name_counter}_tweet.ndjson', 'w') as f:
                        ndjson.dump(tweet_info, f)

                    with open(f'{outpath_user}{json_name}_{querryname}_{name_counter}_user.ndjson', 'w') as f:
                        ndjson.dump(user_info, f)


                    count += result_count
                    total_tweets += result_count
                    print("Total # of Tweets added: ", total_tweets)
                    print("-------------------")
                    time.sleep(5)
                
                #Since this is the final request, turn flag to false to move to the next time period.
                flag = False
                next_token = None
            time.sleep(5)
    print("Total number of results: ", total_tweets)

def main():
    ap = argparse.ArgumentParser(description="[INFO] build graph from nodes and edges")
    ap.add_argument('-mr','--max_results', required=True, help='<int> max results PER querry')
    ap.add_argument('-mc','--max_count', required=True, help='<int> max results per date interval') 
    ap.add_argument('-sd', '--start_dates', required=True, help='<list> list of strings: start dates')
    ap.add_argument('-ed', '--end_dates', required=True, help='<list> list of strings: end dates')
    ap.add_argument("-bt", "--token", required=True, help="path to seed file")
    ap.add_argument("-q", "--querry", required=True, help="paper, abstract or vtt as string")
    ap.add_argument("-qn", "--querryname", required=True, help="paper, abstract or vtt as string")
    ap.add_argument('-ot','--outpath_tweet', required=True, help='outpath for .ndjson main data') 
    ap.add_argument('-ou','--outpath_user', required=True, help='outpath for .ndjson user data') 
    args = vars(ap.parse_args())

    #print(f"{bcolors.OKGREEN}[INFO] drawing graph ...{bcolors.ENDC}")
    def read_arg(argname):
        with open(args[argname], "r") as fobj: 
            argname = fobj.read().splitlines() 
            return argname 

    max_results = args["max_results"]
    max_count = args["max_count"]
    start_dates = read_arg("start_dates")
    end_dates = read_arg("end_dates")
    token = read_arg("token") 
    querry = read_arg("querry")
    querryname = read_arg("querryname")
    outpath_tweet = read_arg("outpath_tweet")
    outpath_user = read_arg("outpath_user")

    print(f"max_results: {max_results}")
    print(f"max_count: {max_count}")
    print(f"start_dates: {start_dates}")
    print(f"end_dates: {end_dates}")
    print(f"token: {token}")
    print(f"querry: {querry}")
    print(f"name: {querryname}")
    print(f"out tweet: {outpath_tweet}")
    print(f"out user: {outpath_user}")

    # main stuff 
    get_tweets(
        start_dates = start_dates, # how does this work? 
        end_dates = end_dates, 
        max_results = max_results, 
        max_count = max_count, 
        querry = querry, 
        querryname = querryname, 
        outpath_tweet = outpath_tweet, 
        outpath_user = outpath_user, 
        bearer_token = token)

if __name__ == '__main__':
    main()