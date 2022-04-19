import sys, backboning, settings
import numpy as np
import pandas as pd
import networkx as nx
from collections import defaultdict

measure_label = {
   "noise_corrected": "Noise-Corrected",
   "disparity_filter": "Disparity Filter",
   "high_salience_skeleton": "High Salience Skeleton",
   "doubly_stochastic": "Doubly Stochastic",
   "maximum_spanning_tree": "Maximum Spanning Tree",
   "naive": "Naive Threshold",
}

country_attributes = pd.read_csv("../country_networks.csv", sep = "\t")
country_population = pd.read_csv("country_pop.csv")
country_attributes = country_attributes.merge(country_population, left_on = "src", right_on = "Country Code", how = "left")
country_attributes = country_attributes.rename(columns = {"2014": "src_pop"}).drop("Country Code", 1)
country_attributes = country_attributes.merge(country_population, left_on = "trg", right_on = "Country Code", how = "left")
country_attributes = country_attributes.rename(columns = {"2014": "trg_pop"}).drop("Country Code", 1)
country_distances = pd.read_csv("cepii_dista.csv", sep = ";")[["iso_o", "iso_d", "comlang_off", "comlang_ethno", "colony", "comcol", "curcol", "col45", "smctry"]]
country_attributes = country_attributes.merge(country_distances, left_on = ["src", "trg"], right_on = ["iso_o", "iso_d"], how = "left")
country_attributes.drop("iso_o", 1, inplace = True)
country_attributes.drop("iso_d", 1, inplace = True)
country_attributes.rename(columns = {"intensity": "fdi"}, inplace = True)
country_eci = pd.read_csv("country_eci.csv", sep = "\t")
country_eci = pd.pivot_table(country_eci, index = "country", columns = "year", values = "eci").reset_index()
country_eci["avg_eci"] = (country_eci[2011] + country_eci[2013]) / 2.0
country_attributes = country_attributes.merge(country_eci[["country", "avg_eci"]], left_on = "src", right_on = "country", how = "left")
country_attributes = country_attributes.rename(columns = {"avg_eci": "src_eci"}).drop("country", 1)
country_attributes = country_attributes.merge(country_eci[["country", "avg_eci"]], left_on = "trg", right_on = "country", how = "left")
country_attributes = country_attributes.rename(columns = {"avg_eci": "trg_eci"}).drop("country", 1)

backbones = defaultdict(lambda : defaultdict(int))
measure_qualities = defaultdict(list)

for network in settings.networks:
   table, original_nodes, original_edges = backboning.read("../country_networks.csv", network, undirected = (network == "cs"))
   for measure in settings.measures:
      edge_table = settings.measures[measure](table, undirected = (network == "cs"))
      if settings.fixedges_thresholds[measure][network] != None:
         edge_table_thresholded = backboning.thresholding(edge_table, settings.fixedges_thresholds[measure][network])
      else:
         edge_table_thresholded = edge_table.copy()
      backbones[measure][network] = edge_table_thresholded
      if not backbones[measure][network].empty:
         G = nx.from_pandas_dataframe(edge_table_thresholded, "src", "trg")
         if network == "mi":
            tmp_table = backbones[measure][network].merge(country_attributes, on = ["src", "trg"])
            base_regr = pd.ols(y = np.log(country_attributes["mi"] + 1), x = {"a": country_attributes[["comlang_off", "comlang_ethno", "colony", "comcol", "curcol", "col45", "smctry"]], "b": np.log(country_attributes[["geodist", "src_pop", "trg_pop"]] + 1)}, intercept = True)
            bb_regr = pd.ols(y = np.log(tmp_table["mi"] + 1), x = {"a": tmp_table[["comlang_off", "comlang_ethno", "colony", "comcol", "curcol", "col45", "smctry"]], "b": np.log(tmp_table[["geodist", "src_pop", "trg_pop"]] + 1)}, intercept = True)
            measure_qualities[measure].append("%1.4f" % (bb_regr.r2 / base_regr.r2))
         elif network == "cs":
            tmp_table = backbones[measure][network].merge(country_attributes, on = ["src", "trg"])
            base_regr = pd.ols(y = np.log(country_attributes["cs"] + 1), x = {"a": country_attributes[["src_eci", "trg_eci"]], "b": np.log(country_attributes[["geodist"]] + 1)}, intercept = True)
            bb_regr = pd.ols(y = np.log(tmp_table["cs"] + 1), x = {"a": tmp_table[["src_eci", "trg_eci"]], "b": np.log(tmp_table[["geodist"]] + 1)}, intercept = True)
            measure_qualities[measure].append("%1.4f" % (bb_regr.r2 / base_regr.r2))

for measure in measure_label:
   print "%s & %s\\\\" % (measure_label[measure], " & ".join(measure_qualities[measure]))
