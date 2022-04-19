import backboning
import pandas as pd

table, original_nodes, original_edges = backboning.read("occupation_occupation_skillcooccurrence", "coocc", triangular_input = True, undirected = True)

table_nc = backboning.noise_corrected(table, undirected = True)
table_df = backboning.disparity_filter(table, undirected = True)

bb_nc = backboning.thresholding(table_nc, 5.0)
bb_df = backboning.thresholding(table_df, 0.87607) # 0.8758

backboning.write(bb_nc[["src", "trg", "score"]], "onet", "nc", ".")
backboning.write(bb_df[["src", "trg", "score"]], "onet", "df", ".")

