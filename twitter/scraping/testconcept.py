import os
import argparse
import numpy as np
from datetime import date
import matplotlib.pyplot as plt

import networkx as nx
#from networkx.drawing.nx_agraph import graphviz_layout
#from community import community_louvain

def main():
    ap = argparse.ArgumentParser(description="[INFO] build graph from nodes and edges")
    ap.add_argument('-mr','--max_results', required=True, help='<int> max results PER querry')
    ap.add_argument('-mc','--max_count', required=True, help='<int> max results per date interval') 
    ap.add_argument('-sd', '--start_dates', required=True, help='<list> list of strings: start dates')
    ap.add_argument('-ed', '--end_dates', required=True, help='<list> list of strings: end dates')
    ap.add_argument("-bt", "--token", required=True, help="path to seed file")
    ap.add_argument("-q", "--querry", required=True, help="paper, abstract or vtt as string")
    ap.add_argument("-qn", "--querryname", required=True, help="paper, abstract or vtt as string")
    ap.add_argument('-ot','--outpath_tweet', required=True, help='outpath for .ndjson main data') 
    ap.add_argument('-ou','--outpath_user', required=True, help='outpath for .ndjson user data') 
    args = vars(ap.parse_args())

    #print(f"{bcolors.OKGREEN}[INFO] drawing graph ...{bcolors.ENDC}")
    def read_arg(argname):
        with open(args[argname], "r") as fobj: 
            argname = fobj.read().splitlines() 
            return argname 

    max_results = args["max_results"]
    max_count = args["max_count"]
    start_dates = read_arg("start_dates")
    end_dates = read_arg("end_dates")
    token = read_arg("token") 
    querry = read_arg("querry")
    querryname = read_arg("querryname")
    outpath_tweet = read_arg("outpath_tweet")
    outpath_user = read_arg("outpath_user")

    print(f"max_results: {max_results}")
    print(f"max_count: {max_count}")
    print(f"start_dates: {start_dates}")
    print(f"end_dates: {end_dates}")
    print(f"token: {token[0]}")
    print(f"querry: {querry[0]}")
    print(f"name: {querryname[0]}")
    print(f"out tweet: {outpath_tweet[0]}")
    print(f"out user: {outpath_user[0]}")

if __name__ == '__main__':
    main()
