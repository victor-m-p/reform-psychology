

import pandas as pd 


# old data
node_old = pd.read_csv("/work/50114/twitter/data/network/backboning/openscience_replicationcrisis_query.csv")
edge_old = pd.read_csv("/work/50114/twitter/data/network/backboning/openscience_replicationcrisis_bb_df_threshold0.99.csv")

# new data
node_new = pd.read_csv("/work/50114/twitter/data/nlp/subsets/os_rc_overlap_authors.csv")
edge_new = pd.read_csv("/work/50114/twitter/data/nlp/backboning/os_rc_overlap_bb_df_threshold0.995.csv")


len(node_old) # 361328
len(edge_old) # 9689

len(node_new) # 393618 (a bit longer)
len(edge_new) # 8777 (a bit shorter)

node_old.head(5)
node_new.head(5)

edge_old.head(5)
edge_new.head(5)

edge_new.head(5)

def edgelist_to_authors(d, from_col, to_col):
    df_src_authors = d[[from_col]]
    df_trg_authors = d[[to_col]].rename(columns = {to_col: from_col})
    df_concat_authors = pd.concat([df_src_authors, df_trg_authors])
    df_authors_edgelist = df_concat_authors.drop_duplicates()
    df_authors_edgelist = df_authors_edgelist.rename(columns = {from_col: 'username'})
    print(len(df_authors_edgelist)) 
    return df_authors_edgelist

unique_nodes = edgelist_to_authors(edge_new, "src", "trg")
node_total = node_new.merge(unique_nodes, on = "username", how = "outer")
node_total["query"] = node_total["query"].fillna("openscience") # just assign openscience (much more likely)

node_total.groupby('query').size()
node_total.head(5)

unique_nodes["query"] = "unknown"
node_total = node_new.merge(unique_no)
check_overlap = node_new.merge(unique_nodes, on = "username", how = "inner")
len(check_overlap)

lst1 = ['openscience', 'replicationcrisis', 'overlap']
lst2 = ['replicationcrisis', 'openscience']
sorting_list = [lst1.index('replicationcrisis'), lst1.index('openscience')]
sorting_list

Z = [x for _,x in sorted(zip(sorting_list,lst2))]
a, b = Z

## check the edgelist 
import pandas as pd 
overlap_edge = pd.read_csv("/work/50114/twitter/data/nlp/edgelists/os_rc_edgelist_overlap.csv")
overlap_edge.isna().sum()
d = overlap_edge
d.isna().sum()