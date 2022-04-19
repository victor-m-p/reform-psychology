import sys, math
import pandas as pd
import backboning
import numpy as np
import networkx as nx
from scipy.stats import sem
from collections import defaultdict

networks = ["cs", "tr", "mi"]

for network in networks:
   sys.stderr.write("%s\n" % network)
   table, original_nodes, original_edges = backboning.read("../country_networks.csv", network)
   weights = defaultdict(list)
   G = nx.from_pandas_dataframe(table, source = "src", target = "trg", edge_attr = "nij")
   for e in G.edges(data = True):
      neigh_edges = G.edges(nbunch = (e[0], e[1]), data = True)
      weights[round(e[2]["nij"])].append(sum(f[2]["nij"] for f in neigh_edges) / len(neigh_edges))
   with open("%s_weight_neighweight" % network, 'w') as f:
      for i in sorted(weights.keys()):
         values = np.array(weights[i])
         mean = np.mean(values)
         if len(values) > 1:
            serr = sem(values)
         else:
            serr = 0
         f.write("%s\t%s\t%s\t%s\n" % (i, mean, mean - serr, mean + serr))
