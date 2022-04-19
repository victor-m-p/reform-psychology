import backboning
from collections import defaultdict

networks = ["cs", "mi", "tr"]

networks_years = {
   "cs": ["cs2011", "cs2012", "cs2013"],
   "tr": ["tr2011", "tr2012", "tr2013"],
   "mi": ["mi1990", "mi2000", "mi2010", "mi2013"],
}

measures = {
   "naive": backboning.naive,
   "noise_corrected": backboning.noise_corrected,
   "disparity_filter": backboning.disparity_filter,
   "doubly_stochastic": backboning.doubly_stochastic,
   "maximum_spanning_tree": backboning.maximum_spanning_tree,
   "high_salience_skeleton": backboning.high_salience_skeleton,
}

edge_set_size = {
   "mi": [   168.        ,    208.70212775,    259.265346  ,    322.07874621,
          400.11023593,    497.04677128,    617.46856404,    767.06549485,
          952.90595774,   1183.77083885,   1470.56840975,   1826.84973881,
         2269.44897365,   2819.27874777,   3502.31829395,   4350.84095245,
         5404.93907314,   6714.4183627 ,   8341.151184  ,  10362.        ],
   "tr": [   165.        ,    213.64201942,    276.62371189,    358.17241471,
          463.76168472,    600.47868395,    777.49987065,   1006.70692402,
         1303.4842437 ,   1687.75155215,   2185.30090836,   2829.52787333,
         3663.67302339,   4743.72426187,   6142.17473256,   7952.88856659,
        10297.40105199,  13333.07609402,  17263.66849571,  22353.        ],
   "cs": [   165.        ,    214.8905632 ,    279.86638881,    364.48876311,
          474.69815507,    618.23123573,    805.16399052,   1048.61905087,
         1365.68689956,   1778.62561821,   2316.42339895,   3016.83350799,
         3929.02455529,   5117.03211834,   6664.25402328,   8679.30485088,
        11303.64065224,  14721.48912734,  19172.78236224,  24970.        ]
}

thresholds = defaultdict(lambda : defaultdict(list))
edgeset_size = defaultdict(lambda : defaultdict(list))
with open("../parameters", 'r') as f:
   for line in f:
      fields = line.strip().split('\t')
      thresholds[fields[0]][fields[1]].append(float(fields[2]))
      if fields[3] != "na":
         edgeset_size[fields[0]][fields[1]].append(int(fields[3]))
      else:
         edgeset_size[fields[0]][fields[1]].append(-1)

fixedges_thresholds = {
   "noise_corrected": {
      "bt": 236,
      "cs": 4.2005,
      "fl": 16012.3,
      "mi": 9750,
      "ow": 965,
      "tr": 301.5,
   },
   "doubly_stochastic": {
      "bt": None,
      "cs": None,
      "fl": None,
      "mi": None,
      "ow": None,
      "tr": None,
   },
   "disparity_filter": {
      "bt": .9996875,
      "cs": .9192,
      "fl": .9832,
      "mi": .9999988,
      "ow": .985,
      "tr": .99999575,
   },
   "high_salience_skeleton": {
      "bt": 0.298,
      "cs": 0.0212,
      "fl": 0.011,
      "mi": 0.08,
      "ow": 0.4,
      "tr": 0.006,
   },
   "naive": {
      "bt": 5850.0,
      "cs": 60.9,
      "fl": 1090000.0,
      "mi": 163300.0,
      "ow": 120.0,
      "tr": 7100,
   },
   "maximum_spanning_tree": {
      "bt": None,
      "cs": None,
      "fl": None,
      "mi": None,
      "ow": None,
      "tr": None,
   },
}
