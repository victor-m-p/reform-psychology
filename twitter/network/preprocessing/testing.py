import pandas as pd 

d = pd.DataFrame({
    'country': [None, 'us', 'us', 'en', None, None, 'ru', 'ba'],
    'id': [1, 1, 2, 2, 3, 3, 4, 4],
    'some_other_col': [1, 2, 3, 4, 5, 6, 7, 8]})

# we expect: 
# us, en/us, None, ru

# (1) subset those with non-nan 
d_notna = d[~d["country"].isnull()][["country", "id"]]
d_na = d.drop(columns='country').drop_duplicates()

# (2) ties in time are extremely unlikely: get most recent 
d_new = d_notna.groupby('id').sample(n = 1, random_state = 113)
d_global = d_new.merge(d_na, on = 'id', how = 'outer')
d_global


d_new = d_notna.sort_values('time', ascending=False).groupby(['id']).first().reset_index()

# (3) merge back in 
d_new.merge(d_na, on = ['id'], how = 'left')

d.groupby()

d_country = d.groupby("id").sample(n=1, random_state=2)
d_country