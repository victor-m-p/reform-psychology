'''
VMP 2022-02-15: checking preprocessed data
'''

## imports  
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import math

## load data
d = pd.read_csv("/work/50114/MAG/data/modeling/psych_replication_matched.csv")

## groups on their own
d_exp = d[d["condition"] == "experiment"]
d_ctrl = d[d["condition"] == "control"]

#### plot c_5 distribution (outcome) ####

## distribution of c_5 for each class
d_exp_c5 = d_exp.groupby('c_5').size().reset_index(name = 'count')
d_ctrl_c5 = d_ctrl.groupby('c_5').size().reset_index(name = 'count')

## cut at 30 to get better overview: 
d_exp_c5_sub = d_exp_c5[d_exp_c5["c_5"] <= 30]
d_ctrl_c5_sub = d_ctrl_c5[d_ctrl_c5["c_5"] <= 30]

# setup mosaic 
figure_mosaic = """
AB
CD
"""

# fig, ax 
fig, ax = plt.subplot_mosaic(mosaic=figure_mosaic, figsize = (10, 10))

# plot all the bars 
ax["A"].bar(d_exp_c5["c_5"], d_exp_c5["count"])
ax["B"].bar(d_ctrl_c5["c_5"], d_ctrl_c5["count"])
ax["C"].bar(d_exp_c5_sub["c_5"], d_exp_c5_sub["count"])
ax["D"].bar(d_ctrl_c5_sub["c_5"], d_ctrl_c5_sub["count"])

# set text 
ax["A"].title.set_text('replication, full')
ax["B"].title.set_text('control, full')
ax["C"].title.set_text('replication, <= 30')
ax["D"].title.set_text('control, <= 30')

# set limits (should be a better way)
# taken from here: https://stackoverflow.com/questions/26454649/python-round-up-to-the-nearest-ten
def round_up(x): 
    return int(math.ceil(x / 10.0)) * 10

ylim_exp = round_up(d_exp_c5["count"].max())
ylim_ctrl = round_up(d_ctrl_c5["count"].max())
ylim_max = max(ylim_exp, ylim_ctrl)

ax["A"].set_ylim(0, ylim_max)
ax["B"].set_ylim(0, ylim_max)
ax["C"].set_ylim(0, ylim_max)
ax["D"].set_ylim(0, ylim_max)

# plt show 
plt.show();



def plot_outcome(): 
    fig, ax = plt.subplots(2)


