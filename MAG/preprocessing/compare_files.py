import pandas as pd 
import seaborn as sns 
import matplotlib.pyplot as plt 


# load files
df_old = pd.read_csv("/work/50114/MAG/data/modeling/psych_replication_matched.csv")
df_new = pd.read_csv("/work/50114/MAG/data/modeling_new/psychology_replicat_matched.csv")

len(df_old)
len(df_new)

df_old.head(5)
df_new.head(5)

sns.lmplot(
    data = df_old, 
    x = "n_authors",
    y = "c_5",
    hue = 'condition')

sns.lmplot(
    data = df_new, 
    x = 'n_authors',
    y = 'c_5',
    hue = 'condition'
)

# what are those crazy-big studies?
