import numpy as np
import pandas as pd

def backbone_restriction(backbone):
   bb = pd.read_csv("onet_%s.csv" % backbone, sep = "\t")
   bb_rev = bb.copy()
   bb_rev.rename(columns = {"src": "trg", "trg": "src"}, inplace = True)
   bb = pd.concat([bb, bb_rev[bb_rev["src"] != bb_rev["trg"]]])
   bb = bb.merge(jumps, on = ["src", "trg"]).fillna(0)
   regr = pd.ols(y = bb["jumps"], x = bb[["coocc", "jumps_srcsum", "jumps_trgsum"]])
   print backbone, regr.r2 ** .5

coocc = pd.read_csv("occupation_occupation_skillcooccurrence", sep = "\t")
coocc_rev = coocc.copy()
coocc_rev.rename(columns = {"src": "trg", "trg": "src"}, inplace = True)
coocc = pd.concat([coocc[coocc["src"] != coocc["trg"]], coocc_rev[coocc_rev["src"] != coocc_rev["trg"]]])
occupations = set(coocc["src"]) | set(coocc["trg"])

jumps = pd.read_csv("job_mobility_network_09_10_onet", sep = "\t")
jumps = jumps[(jumps["src"].isin(occupations)) & (jumps["trg"].isin(occupations))]
jumps = jumps[jumps["src"] != jumps["trg"]]
source_sizes = jumps.groupby(by = "src").sum().reset_index()
target_sizes = jumps.groupby(by = "trg").sum().reset_index()
jumps = jumps.merge(source_sizes, on = "src", suffixes = ("", "_srcsum"))
jumps = jumps.merge(target_sizes, on = "trg", suffixes = ("", "_trgsum"))

jumps = jumps.merge(coocc, on = ["src", "trg"], how = "left").fillna(0)

regr = pd.ols(y = jumps["jumps"], x = jumps[["coocc", "jumps_srcsum", "jumps_trgsum"]])

print regr.r2 ** .5
backbone_restriction("df")
backbone_restriction("nc")
