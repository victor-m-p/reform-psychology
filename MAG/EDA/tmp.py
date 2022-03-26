import pandas as pd 

# check replication
key_rep = pd.read_csv("/work/50114/MAG/data/modeling/psychology_replicat_matched.csv")
fos_rep = pd.read_csv("/work/50114/MAG/data/modeling/psychology_replication_matched.csv")

# wow, huge difference
key_rep.groupby('condition')['c_5'].mean()
fos_rep.groupby('condition')['c_5'].mean()

# check other keywords
fos_reproduce = pd.read_csv("/work/50114/MAG/data/modeling/psychology_reproducibility_matched.csv")
fos_reproduce.groupby('condition')['c_5'].mean()

# model BOTH replication & reproducibility 
