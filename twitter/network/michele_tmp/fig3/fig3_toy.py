import backboning
import pandas as pd

toy_table = pd.read_csv("toy_net", sep = "\t")
table_nc = backboning.noise_corrected(toy_table, undirected = True)
table_df = backboning.disparity_filter(toy_table, undirected = True)

bb_neffke = backboning.thresholding(table_nc, 4)
bb_vespignani = backboning.thresholding(table_df, 0.66)

print "NC Backbone:"
print bb_neffke
print
print "DF Backbone:"
print bb_vespignani
