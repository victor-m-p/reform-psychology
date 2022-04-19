import sys, random, backboning
import numpy as np
import pandas as pd
import networkx as nx
from scipy.stats import sem
from collections import defaultdict

def find_bb_for_nedges(table, n, starting_guess, step):
   cur_threshold = starting_guess
   edge_table_thresholded = backboning.thresholding(table, cur_threshold)
   back = False
   forth = False
   try:
      while edge_table_thresholded.shape[0] != n:
         old_threshold = cur_threshold
         old_edge_table_thresholded = edge_table_thresholded.copy()
         if edge_table_thresholded.shape[0] > n:
            cur_threshold += step
            forth = True
         else:
            cur_threshold -= step
            back = True
         edge_table_thresholded = backboning.thresholding(table, cur_threshold)
         if back and forth:
            break
   except KeyboardInterrupt:
      return old_edge_table_thresholded
   try:
      if abs(n - old_edge_table_thresholded.shape[0]) < abs(n - edge_table_thresholded.shape[0]):
         return old_edge_table_thresholded
      else:
         return edge_table_thresholded
   except UnboundLocalError:
      return edge_table_thresholded

def generate_edges():
   G = nx.barabasi_albert_graph(nnodes, 3)
   degrees = G.degree()
   edges = nx.to_pandas_dataframe(G).unstack().reset_index().rename(columns = {"level_0": "src", "level_1": "trg", 0: "nonoise"})
   edges["nij"] = edges.apply(lambda x : (degrees[x["src"]] + degrees[x["trg"]]) * abs(np.random.uniform(low = amount_of_noise, high = 1.0)) if x["nonoise"] == 1 else (degrees[x["src"]] + degrees[x["trg"]]) * abs(np.random.uniform(low = 0.0, high = amount_of_noise)), axis = 1)
   return edges

def make_columns(jaccards):
   if len(jaccards) > 0:
      array = np.array(jaccards)
      mean = np.mean(array)
      serr = np.std(array)
      return "%1.4f\t%1.4f\t%1.4f" % (mean, mean - serr, mean + serr)
   else:
      return "na\tna\tna"

nnodes = int(sys.argv[1])
runs = int(sys.argv[2])

with open("fig4_data", 'w') as f:
   for amount_of_noise in (0, 0.025, 0.05, 0.075, 0.1, 0.125, 0.15, 0.175, 0.2, 0.225, 0.25, 0.275):
      sys.stderr.write("%s\n" % amount_of_noise)
      method_jaccards = defaultdict(list)
      for _ in range(runs):
         edges = generate_edges()
         n_true_edges = edges["nonoise"].sum() / 2
         table_noise_corrected = backboning.noise_corrected(edges, undirected = True)
         table_disparity_filter = backboning.disparity_filter(edges, undirected = True)
         #table_high_salience_skeleton = backboning.high_salience_skeleton(edges, undirected = True) # WARNING: REALLY SLOW! Comment out for significant speedup (but no HSS backbone will be generated)
         table_naive = backboning.naive(edges, undirected = True)
         bb_noise_corrected = find_bb_for_nedges(table_noise_corrected, n_true_edges, 1, .05)
         bb_disparity_filter = find_bb_for_nedges(table_disparity_filter, n_true_edges, 1, .0004)
         #bb_high_salience_skeleton = find_bb_for_nedges(table_high_salience_skeleton, n_true_edges, 0, .0001) # WARNING: REALLY SLOW! Comment out for significant speedup (but no HSS backbone will be generated)
         bb_naive = find_bb_for_nedges(table_naive, n_true_edges, 0, .5)
         bb_maximum_spanning_tree = backboning.maximum_spanning_tree(edges, undirected = True)
         #bb_doubly_stochastic = backboning.doubly_stochastic(edges, undirected = True)
         method_jaccards["noise_corrected"].append(backboning.stability_jac(bb_noise_corrected, edges[(edges["nonoise"] == 1) & (edges["src"] < edges["trg"])]))
         method_jaccards["disparity_filter"].append(backboning.stability_jac(bb_disparity_filter, edges[(edges["nonoise"] == 1) & (edges["src"] < edges["trg"])]))
         #method_jaccards["high_salience_skeleton"].append(backboning.stability_jac(bb_high_salience_skeleton, edges[(edges["nonoise"] == 1) & (edges["src"] < edges["trg"])])) # WARNING: REALLY SLOW! Comment out for significant speedup (but no HSS backbone will be generated)
         method_jaccards["naive"].append(backboning.stability_jac(bb_naive, edges[(edges["nonoise"] == 1) & (edges["src"] < edges["trg"])]))
         method_jaccards["maximum_spanning_tree"].append(backboning.stability_jac(bb_maximum_spanning_tree, edges[(edges["nonoise"] == 1) & (edges["src"] < edges["trg"])]))
         #if not bb_doubly_stochastic.empty:
         #   method_jaccards["doubly_stochastic"].append(backboning.stability_jac(bb_doubly_stochastic, edges[(edges["nonoise"] == 1) & (edges["src"] < edges["trg"])]))
      line = []
      line.append(str(amount_of_noise))
      line.append(make_columns(method_jaccards["noise_corrected"]))
      line.append(make_columns(method_jaccards["disparity_filter"]))
      line.append(make_columns(method_jaccards["naive"]))
      line.append(make_columns(method_jaccards["maximum_spanning_tree"]))
      #line.append(make_columns(method_jaccards["doubly_stochastic"]))
      #line.append(make_columns(method_jaccards["high_salience_skeleton"])) # WARNING: REALLY SLOW! Comment out for significant speedup (but no HSS backbone will be generated)
      f.write("%s\n" % '\t'.join(line))
      f.flush()
