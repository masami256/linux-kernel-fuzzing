#!/usr/bin/env python3

import argparse
import sys
import os
import glob
import json
import re

import pprint

def count_function_calls(cg_data):
    for bc_filename in cg_data:
        for caller in cg_data[bc_filename]:
            for sl in cg_data[bc_filename][caller]:
                if sl == "FunctionCalls":
                    continue

                if cg_data[bc_filename][caller][sl]["icall"]:
                    cg_data[bc_filename][caller]["FunctionCalls"]["TotalIndirectCalls"] += 1
                else:
                    cg_data[bc_filename][caller]["FunctionCalls"]["TotalDirectCalls"] += 1
            cg_data[bc_filename][caller]["FunctionCalls"]["TotalCalls"] = \
                cg_data[bc_filename][caller]["FunctionCalls"]["TotalIndirectCalls"] + cg_data[bc_filename][caller]["FunctionCalls"]["TotalDirectCalls"]

    return cg_data

def read_callgraph_json(directory_path):
    cg_data = {}
    restr = r"-(.*?)[.]"
    paths = directory_path.split("/")
    idx = paths.index("bcfiles") + 1
    paths = "/".join(paths[idx:])

    json_files = glob.glob(os.path.join(directory_path, '**', 'callgraph-*.json'), recursive=True)
    for j in json_files:
        tmp = j.split("/")
        paths = "/".join(tmp[idx:len(tmp) -1])
        bc_filename = os.path.abspath(directory_path + paths + "/" + re.search(restr, os.path.basename(j)).group(1) + ".bc")

        cg_data[bc_filename] = {}

        with open(j) as f:
            module_data = json.load(f)

        for d in module_data:
            caller = d["CallerName"]
            srcline = d["SourceLine"]

            if not caller in cg_data[bc_filename]:
                cg_data[bc_filename][caller]= {
                    "FunctionCalls": {
                        "TotalCalls": 0,
                        "TotalIndirectCalls": 0,
                        "TotalDirectCalls": 0,
                    },
                }
                
            if not srcline in cg_data[bc_filename][caller]:
                cg_data[bc_filename][caller][srcline] = {
                    "icall": False,
                    "dcall": False,
                }
                if d["isIndirectCall"]:
                    cg_data[bc_filename][caller][srcline]["icall"] = True
                else:
                    cg_data[bc_filename][caller][srcline]["dcall"] = True
    
    return count_function_calls(cg_data)


def parse_options():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bcfiles-dir", help="path to bcfiles", required=True,
                        metavar="BCFILES_DIR")
    parser.add_argument("--memory-ops-json", help="memory operation json", required=True,
                        metavar="MEMORY_OPS_JSON")  
    parser.add_argument("--bb-info-json", help="BasicBlock information json", required=True,
                        metavar="BB_INFO_JSON")  
    
    args = parser.parse_args()
    return args

def main():
    args = parse_options()
    
    cg_data = read_callgraph_json(args.bcfiles_dir)

    pprint.pprint(cg_data)

if __name__ == "__main__":
    main()
