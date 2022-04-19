import community
import numpy as np
import networkx as nx
from sklearn.metrics import normalized_mutual_info_score, adjusted_mutual_info_score

def load_infomap_comms(filename):
   nodemap = {}
   with open("%s.map" % filename, 'r') as f:
      for line in f:
         fields = line.strip().split('\t')
         nodemap[fields[0]] = fields[1]
   partition = {}
   with open("%s.tree" % filename, 'r') as f:
      next(f)
      next(f)
      for line in f:
         fields = line.strip().split()
         comms = fields[0].strip().split(':')
         partition[nodemap[fields[-1]]] = comms[0]
   return partition

def calculate_modularity(netname, delimiter = "\t"):
   G = nx.read_edgelist("%s.csv" % netname, delimiter = delimiter, data = [("w", float)], comments = "s")
   partition = {}
   for n in G.nodes():
      partition[n] = n[:2]
   modularity = community.modularity(partition, G)
   partition_infomap = load_infomap_comms(netname)
   x = []
   y = []
   nodes = sorted(list(set(partition.keys()) & set(partition_infomap.keys())))
   for n in nodes:
      x.append(partition[n])
      y.append(partition_infomap[n])
   print netname
   print modularity
   print normalized_mutual_info_score(np.array(x), np.array(y))

calculate_modularity("onet_nc")
calculate_modularity("onet_df")
