import pandas as pd 
import json 

with open('/work/50114/twitter/data/json/2010-01-01_openscience_1_tweet.json') as d:
    dictData = json.load(d)

for i in range(50):
    try: 
        dictData.get('data')[i]["geo"]
    except: 
        pass 
dictData.get('data') # one dictionary 
dictData.get('includes').get('users') 
dictData.get('includes').get('places')