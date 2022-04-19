import backboning, settings
import pandas as pd
import numpy as np
from scipy.stats import pearsonr, sem
from collections import defaultdict

country_attributes = pd.read_csv("../country_networks.csv", sep = "\t")

ndigits = {"cs": 2, "mi": 3, "tr": 3}

print "Noise Corrected"
for network in settings.networks_years:
   obs_variance_cij = pd.DataFrame(columns = ["src", "trg", "score"])
   for year in settings.networks_years[network]:
      table, _, _ = backboning.read("../country_networks.csv", year)
      nc_table = backboning.noise_corrected(table)
      obs_variance_cij = obs_variance_cij.merge(nc_table[["src", "trg", "score"]], on = ["src", "trg"], how = "right", suffixes = ("", "_%s" % year))
   obs_variance_cij = obs_variance_cij.drop("score", 1).dropna()
   obs_variance_cij["sdev_cij"] = obs_variance_cij.std(axis = 1)
   table, _, _ = backboning.read("../country_networks.csv", network)
   nc_table = backboning.noise_corrected(table)
   nc_table = nc_table[["src", "trg", "sdev_cij"]].merge(obs_variance_cij[["src", "trg", "sdev_cij"]], on = ["src", "trg"])
   nc_table["sdev_cij_x_agg"] = nc_table["sdev_cij_x"].round(decimals = ndigits[network]) + (10 ** -ndigits[network])
   nc_table["sdev_cij_y_agg"] = nc_table["sdev_cij_y"].round(decimals = ndigits[network]) + (10 ** -ndigits[network])
   sdev_cij_y_cnt = nc_table.groupby(by = ["sdev_cij_x_agg", "sdev_cij_y_agg"])["sdev_cij_y"].count().reset_index()
   sdev_cij_y_cnt.sort_values(by = "sdev_cij_y").to_csv("sdev_%s_noise_corrected" % network, index = False, sep = "\t")
   corr = pearsonr(np.log(nc_table["sdev_cij_x"]), np.log(nc_table["sdev_cij_y"]))
   print "%s\t%s\t%s" % (network, corr[0], corr[1])

