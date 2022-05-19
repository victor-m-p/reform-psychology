"""
nonnegfac implementation of NMF

VMP: seems like the main document. 

TODO: 
* check results 
* add K to output name. 
"""

import argparse
import os
import pandas as pd
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from nonnegfac.nmf import NMF
from sklearn.metrics import pairwise_distances
import time 

def display_topics(H, feature_names, no_top_words, filename="dimensions.txt"):
    """ display no_top_words number of words for each topic in a sklearn latent variable model
    """
    with open(filename, "a") as fname:
        for topic_idx, topic in enumerate(H):
            #print(f"dimension {topic_idx}:")
            s = f"dimension-{topic_idx}: " + " ".join([feature_names[i]+", "
                        for i in topic.argsort()[:-no_top_words - 1:-1]])
            print(s)
            fname.write(f"{s}\n")

def main(inpath, outpath, textcol, k):
    t0 = time.perf_counter()
    print(f"--- starting: msg decomposition ---")
    data = pd.read_csv(inpath)
    data = data[~data[textcol].isnull()] # a few null values (which breaks it). 
    content_norm = data[textcol].values # the column?
    print(content_norm)

    from sklearn.feature_extraction import text
    swfilter = text.ENGLISH_STOP_WORDS.union() # already did stopwords?
    
    no_features = 2500 # is this a good number?
    print(f"[INFO] contructing vector model with {no_features} features")

    vectorizer = TfidfVectorizer(
        max_features = no_features,
        ngram_range = (1,1),
        max_df = .25,
        stop_words = swfilter
        )

    # decomposition
    print(f"--> main decomposition")
    X = vectorizer.fit_transform(content_norm)
    features = vectorizer.get_feature_names_out() # was get_feature_names() but deprecated
    print("[INFO] decomposing DT matrix...")
    np.random.seed(1234)
    W, H, info = NMF().run(X, k, max_iter = 100, verbose=0)

    # logging topics
    outname = re.search("by_tweet/(.*).csv", inpath)[1]
    logname = f'{outpath}{outname}_k{k}_log.txt'
    print(f"[INFO] wrting model log to {logname}")
    with open(logname, "w") as fname:
        for (key, value) in info.items():
            fname.write(f"{key}: {value}\n")
    display_topics(H.T, features, k, filename=logname)   

    # logging w  
    np.savetxt(f'{outpath}{outname}_k{k}_W.txt', W, fmt="%.5f")
    print(f"[INFO] wrting W to {outpath}")
    t1 = time.perf_counter()
    t_total = t1 - t0
    print(f"time total: {round(t_total/60, 2)} minutes")
    # nmf (pairwise)
    #print(f"--> pairwise distance")
    #D = pairwise_distances(W, metric = "cosine")
    #np.savetxt(f'{outpath}{outname}_k{k}_D.txt', D, fmt="%.5f")
    #print(f"[INFO] writing D to {outpath}")

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--inpath", required=True, type=str, help="path to csv")
    ap.add_argument("-o", "--outpath", required=True, type=str, help="path to folder for output csv")
    ap.add_argument("-t", "--textcol", required=True, type=str, help="column name containing text")
    ap.add_argument("-k", "--k", required=True, type=int, help="number of topics")
    args = vars(ap.parse_args())

    main(
        inpath = args["inpath"], 
        outpath = args["outpath"], 
        textcol = args["textcol"],
        k = args["k"])

