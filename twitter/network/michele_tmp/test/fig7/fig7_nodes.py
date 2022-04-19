import sys, backboning, settings
import pandas as pd
import networkx as nx
from collections import defaultdict

for network in settings.networks:
   table, original_nodes, original_edges = backboning.read("../country_networks.csv", network, undirected = (network == "cs"))
   for measure in settings.measures:
      with open("%s_%s" % (network, measure), 'w') as f:
         edge_table = settings.measures[measure](table, undirected = (network == "cs"))
         for i in range(len(settings.thresholds[measure][network])):
            if settings.thresholds[measure][network][i] != float("inf"):
               edge_table_thresholded = backboning.thresholding(edge_table, settings.thresholds[measure][network][i])
            else:
               edge_table_thresholded = edge_table.copy()
            if "src" in edge_table_thresholded:
               number_of_nodes = len(set(edge_table_thresholded["src"]) | set(edge_table_thresholded["trg"]))
               f.write("%s\t%s\n" % (float(edge_table_thresholded.shape[0]) / original_edges, float(number_of_nodes) / original_nodes))
