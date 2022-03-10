'''
VMP 2022-03-10: 
Checks 
(1) matching 
(2) manually checks studies
'''

# imports 
import pandas as pd 

# load files
field = 'psychology'
query = 'replicat'
df_preprocessed = pd.read_csv(f"/work/50114/MAG/data/modeling_new/{field}_{query}_matched.csv")

''' total number of matched records ''' 
df_length = len(df_preprocessed)
df_matched = int(df_length/2)
df_matched_check = df_preprocessed["match_group"].max()

# print information: 
print(f"number of datapoints: {df_length}")
print(f"number of matched records: {df_matched}")
print(f"number of matched (double-check): {df_matched_check}")

# function to check matching
def check_matching(df, col, n_matched):
    '''
    df: <pd.dataframe> 
    col: <str> column name
    n_matched: <int> number of total matched records
    ''' 
    df = df.groupby(['match_group', col]).size().reset_index(name = 'count')
    df = df[df["count"] == 2]
    df_len = len(df)
    print(f"N pairs matched perfectly on {col}: {df_len} ({n_matched}) --> {round(df_len/n_matched*100, 2)}%")

# actually check matching 
check_matching(df_preprocessed, "Year", df_matched)
check_matching(df_preprocessed, "n_authors", df_matched)
check_matching(df_preprocessed, "DocType", df_matched)

# manually check studies: 
