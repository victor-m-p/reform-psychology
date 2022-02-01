import pandas as pd 

### check that the number of tweets is correct: 
clean_tweets = pd.read_csv("/work/50114/twitter/data/nlp/NLP2CSV.csv")
clean_tweets.head(5) # right columns 
len(clean_tweets) # 4894 from 21K tweets (& still some duplication). 
tweets = pd.read_csv("/work/50114/twitter/data/network/openscience_tweet.csv")
orig_tweets = tweets[tweets["tweet_type"].isin(["original", "replied_to"])]
len(orig_tweets) # 4894 (so correct.)

'''
number of tweets: correct
'''

### check that they are cleaned properly. 
clean_tweets.head(10)

'''
cleaning: ok I think. 
* stopwords? (i.e. "of", "a", etc.)
* spaces / hyphen? 
* handles (e.g. @TomReller --> tomreller) -- perhaps ok. 
* not great at removing https://t.co.... 
'''
