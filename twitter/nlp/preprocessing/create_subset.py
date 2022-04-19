'''
VMP 2022-04-18: 
Only the intersection of Open Science & Replication Crisis (perhaps incl. all of replication crisis). 
Perhaps this will be generalized, but likely not. 
'''

import pandas as pd 
import numpy as np 
import pickle 

# read labels file (from the network pipeline)
## these have either (a) retweeted or (b) authored in both categories. 
d_labelled = pd.read_csv("/work/50114/twitter/data/network/backboning/openscience_replicationcrisis_query.csv")

# read original data 
repcrisis = "/work/50114/twitter/data/raw/preprocessed/replicationcrisis.pickle"
opensci = "/work/50114/twitter/data/raw/preprocessed/openscience.pickle"

with open(f"{repcrisis}", "rb") as f:
    dct_repcrisis = pickle.load(f)

with open(f"{opensci}", "rb") as f: 
    dct_opensci = pickle.load(f)

# convert to dataframe
d_repcrisis = pd.DataFrame.from_dict(dct_repcrisis)
d_opensci = pd.DataFrame.from_dict(dct_opensci)

# check stuff
d_intersection = d_labelled[d_labelled["query"] == "Overlap"]
d_intersection = d_intersection.rename(columns = {'user': 'main_author_username'})

# inner join on user
d_repcrisis_sub = d_repcrisis.merge(d_intersection, on = 'main_author_username', how = 'inner')
d_opensci_sub = d_opensci.merge(d_intersection, on = 'main_author_username', how = 'inner')

## NB: still have more than half of replication crisis (77K --> 41K)
## NB: less than half of openscience after subset (2M --> 600K)

# now concatenate those two: 
d_intersection_clean = pd.concat([d_repcrisis_sub, d_opensci_sub])

# convert to dictionary 
d_intersection_dct = d_intersection_clean.to_dict()

# save as pickle 
outpath = "/work/50114/twitter/data/nlp/subsets"
filename = "openscience_replicationcrisis_intersection"
with open(f'{outpath}/{filename}.pickle', 'wb') as handle:
    pickle.dump(d_intersection_dct, handle, protocol=pickle.HIGHEST_PROTOCOL)
