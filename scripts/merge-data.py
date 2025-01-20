#!/usr/bin/env python3

import argparse
import sys
import os
import glob
import json
import re

import pprint

def sort_by_bbcount_and_memory_ops(data):
    results = []
    for file_path, functions in data.items():
        for func_name, metrics in functions.items():
            bbcount = metrics.get('bbcount', 0)
            memory_ops_total = metrics.get('memory_ops', {}).get('total', 0)
            results.append((file_path, func_name, bbcount, memory_ops_total))
    
    results.sort(key=lambda x: (x[2], x[3]), reverse=True)
    return results

def merge_data(cg_data, memory_ops, bb_info):
    merged = {}

    for moduleName in cg_data:
        merged[moduleName] = {}
        if moduleName in memory_ops:
            for functionName in memory_ops[moduleName]:
                alloc_cnt = len(memory_ops[moduleName][functionName]["alloc"]) if memory_ops[moduleName][functionName]["alloc"] else 0
                free_cnt = len(memory_ops[moduleName][functionName]["free"]) if memory_ops[moduleName][functionName]["free"] else 0

                merged[moduleName][functionName] = {
                    "memory_ops": {
                        "alloc": alloc_cnt,
                        "free": free_cnt,
                        "total": alloc_cnt + free_cnt,
                    }
                }

                if moduleName in bb_info:
                    if functionName in bb_info[moduleName]:
                        merged[moduleName][functionName]["bbcount"] = bb_info[moduleName][functionName]["BasicBlocks"]
                        merged[moduleName][functionName]["CallInst"] = cg_data[moduleName][functionName]["FunctionCalls"]

        if not merged[moduleName]:
            del merged[moduleName]
    
    return sort_by_bbcount_and_memory_ops(merged)

def read_bb_info_json(bb_info_json):
    with open(bb_info_json) as f:
        bb_info = json.load(f)
    return bb_info

def read_memory_ops_json(memory_ops_json):
    with open(memory_ops_json) as f:
        memory_ops = json.load(f)
    return memory_ops

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

        with open(j) as f:
            module_data = json.load(f)
        
        # ignore empty data
        if not module_data:
            continue

        cg_data[bc_filename] = {}

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
    parser.add_argument("--output", help="Output file name", required=False,
                        metavar="OUTPUT_FILE_NAME", default="output")  
    args = parser.parse_args()
    return args

def main():
    args = parse_options()
    
    cg_data = read_callgraph_json(args.bcfiles_dir)
    memory_ops = read_memory_ops_json(args.memory_ops_json)
    bb_info = read_memory_ops_json(args.bb_info_json)

    
    result = merge_data(cg_data, memory_ops, bb_info)

    output_csv = args.output + ".csv"
    output_json = args.output + ".json"

    with open(output_json, "w") as f:
        json.dump(result, f, indent=4)

    with open(output_csv, "w") as f:
        for r in result:
            f.write(f"{r[0]},{r[1]},{r[2]},{r[3]}\n")
        
    print(f"Output written to {output_json} and {output_csv}")
if __name__ == "__main__":
    main()
