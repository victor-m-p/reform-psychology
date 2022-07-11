

import pandas as pd 

# read files 
d_eigen = pd.read_csv("/work/50114/twitter/data/nlp/centrality_report/eigenvector.csv")
d_weight = pd.read_csv("/work/50114/twitter/data/nlp/centrality_report/weighted_degree.csv")

# combine files 
d_eigen = d_eigen[["username", "eigenvector", "rank"]]
d_weight = d_weight[["username", "weighted_degree", "rank"]]
d_eigen = d_eigen.rename(columns = {'rank': 'rank_eigen'})
d_weight = d_weight.rename(columns = {'rank': 'rank_weight'})
d_total = d_eigen.merge(d_weight, on = ['username'], how = 'inner')
d_total = d_total.assign(weight_minus_eigen = lambda x: x["rank_weight"] - x["rank_eigen"])
# 249 accounts only (after backboning) 

d_total.sort_values("weight_minus_eigen").head(20)

# theory accounts:
## o_guest (Olivia Guest)
## EikoFried (Eiko Fried) -- Smaldino is not there
## zerdeve (Berna Devezer)
## IrisVanRooij (Iris Van Rooij)

account_list = ["psmaldino", "djnavarro", "o_guest", "EikoFried", "zerdeve", "IrisVanRooij"]
d_focus = d_total[d_total["username"].isin(account_list)]


## how did we get so far down?
import pandas as pd
import pickle
orig_edgelist = "/work/50114/twitter/data/nlp/edgelists/os_rc_5_edgelist_intersection.pickle"
comm_edgelist = "/work/50114/twitter/data/nlp/semantic_info/semantic_edgelist.pickle"
backboned_edgelist = "/work/50114/twitter/data/nlp/backboning/os_rc_5_intersection_bb_df_threshold0.9.pickle"

with open(f"{orig_edgelist}", "rb") as f:
    dct = pickle.load(f)
df_edge_orig = pd.DataFrame.from_dict(dct)

with open(f"{orig_edgelist}", "rb") as f:
    dct = pickle.load(f)
df_edge_comm = pd.DataFrame.from_dict(dct)

with open(f"{backboned_edgelist}", "rb") as f:
    dct = pickle.load(f)
df_edge_bb = pd.DataFrame.from_dict(dct)

df_edge_orig.head(5)
df_edge_bb.head(5)

def edgelist_to_authors(d, from_col, to_col):
    df_src_authors = d[[from_col]]
    df_trg_authors = d[[to_col]].rename(columns = {to_col: from_col})
    df_concat_authors = pd.concat([df_src_authors, df_trg_authors])
    df_authors_edgelist = df_concat_authors.drop_duplicates()
    df_authors_edgelist = df_authors_edgelist.rename(columns = {from_col: 'username'})
    print(len(df_authors_edgelist)) 
    return df_authors_edgelist

df_edge_orig_authors = edgelist_to_authors(df_edge_orig, "username_from", "username_to")
df_edge_comm_authors = edgelist_to_authors(df_edge_comm, "username_from", "username_to") # 663 (why not 800?)
df_edge_bb_authors = edgelist_to_authors(df_edge_bb, "src", "trg") # 275 (sure...)

df_edge_orig_authors.head(10)