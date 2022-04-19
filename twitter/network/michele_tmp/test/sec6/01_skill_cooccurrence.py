import numpy as np
import pandas as pd

occupations = pd.read_csv("occupation_attributes", sep = "\t")
occupations = set(occupations["occ"])

table1 = pd.read_csv("skills_abilities", sep = "\t", header = None, names = ["occupation", "skill", "skillname", "importance type", "intensity", "raters", "sd", "int low", "int high", "flag1", "flag2", "date", "author"])
table2 = pd.read_csv("skills_knowledge", sep = "\t", header = None, names = ["occupation", "skill", "skillname", "importance type", "intensity", "raters", "sd", "int low", "int high", "flag1", "flag2", "date", "author"])
table3 = pd.read_csv("skills_skills", sep = "\t", header = None, names = ["occupation", "skill", "skillname", "importance type", "intensity", "raters", "sd", "int low", "int high", "flag1", "flag2", "date", "author"])
table4 = pd.read_csv("skills_tooltech", sep = "\t", header = None, names = ["occupation", "occupation name", "skill type", "skill name", "skill", "skill category"])
table5 = pd.read_csv("tasks_dwa", sep = "\t", header = None, names = ["occupation", "task"])

table = pd.concat([table1, table2, table3])

table["occupation"] = table["occupation"].str[:-3]
table = table[table["occupation"].isin(occupations)]
table = table[["occupation", "skill", "importance type", "intensity"]].groupby(by = ["occupation", "skill", "importance type"]).mean().reset_index()
avg_intensity = table.groupby(by = ["skill", "importance type"]).mean().reset_index()
table = table.merge(avg_intensity, on = ["skill", "importance type"], suffixes = ("", " avg"))
table = table[table["intensity"] > table["intensity avg"]]
table = table.groupby(by = ["occupation", "skill"]).count().reset_index()
table = table[table["intensity"] == 2][["occupation", "skill"]]

table4["occupation"] = table4["occupation"].str[:-3]
table4 = table4[table4["occupation"].isin(occupations)]
table4 = table4[["occupation", "skill"]].groupby(by = ["occupation", "skill"]).count().reset_index()

table5["occupation"] = table5["occupation"].str[:-3]

table = pd.concat([table, table4, table5])
table["present"] = 1
table = pd.pivot_table(table, index = "skill", columns = "occupation", values = "present", aggfunc = "count", fill_value = 0)

coocc = table.T.dot(table)
#np.fill_diagonal(coocc.values, 0)
coocc = coocc.unstack()
coocc.index.names = ["src", "trg"]
coocc = coocc.reset_index()
coocc = coocc[(coocc["src"] <= coocc["trg"]) & (coocc[0] > 0)]
coocc.rename(columns = {0: "coocc"}, inplace = True)
coocc.to_csv("occupation_occupation_skillcooccurrence", index = False, sep = "\t")
