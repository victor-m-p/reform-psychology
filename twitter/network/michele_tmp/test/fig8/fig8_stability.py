import sys, backboning, settings
import pandas as pd
import networkx as nx
from collections import defaultdict

country_attributes = pd.read_csv("../country_networks.csv", sep = "\t")

for network_cl in settings.networks_years:
   tables = []
   full_table, original_nodes, original_edges = backboning.read("../country_networks.csv", network_cl, undirected = (network_cl == "cs"))
   for network in settings.networks_years[network_cl]:
      table, _, _ = backboning.read("../country_networks.csv", network, undirected = ("cs" in network))
      table["edge"] = table.apply(lambda x: "%s-%s" % (x["src"], x["trg"]), axis = 1)
      tables.append(table)
   for measure in settings.measures:
      with open("%s_%s" % (network_cl, measure), 'w') as f:
         edge_tables = [settings.measures[measure](table, undirected = (network_cl == "cs")) for table in tables]
         for i in range(len(settings.edgeset_size[measure][network_cl])):
            if settings.thresholds[measure][network_cl][i] != float("inf"):
               edge_tables_thresholded = [backboning.thresholding(edge_table, settings.thresholds[measure][network_cl][i]) for edge_table in edge_tables]
            else:
               edge_tables_thresholded = [edge_table.copy() for edge_table in edge_tables]
            stabilities = []
            if not edge_tables_thresholded[0].empty:
               for j in range(len(tables) - 1):
                  stabilities.append(backboning.stability_corr(edge_tables_thresholded[j], edge_tables_thresholded[j + 1]))
            if len(stabilities) > 0:
               f.write("%s\t%s\n" % (float(settings.edgeset_size[measure][network_cl][i]) / original_edges, sum(stabilities) / len(stabilities)))


