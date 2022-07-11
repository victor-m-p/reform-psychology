import pandas as pd 
import pickle
pd.set_option('display.max_colwidth', None)

with open(f"/work/50114/twitter/data/raw/preprocessed/replicationcrisis.pickle", "rb") as f:
    d = pickle.load(f)

df = pd.DataFrame.from_dict(d)
df = df[["type_tweet", "main_text"]]

replied = df[df["type_tweet"] == "replied_to"]
quoted = df[df["type_tweet"] == "quoted"]
quoted.head(10)