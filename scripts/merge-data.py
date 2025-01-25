#!/usr/bin/env python3

import argparse
import sys
import os
import glob
import json
import re

import pprint


def merge_data_by_file(merged_by_function_data):
    result = {} 
    
    for bcfile in merged_by_function_data:
        if not bcfile in result:
            icalls = sum([v.get("FunctionCalls", {}).get("TotalIndirectCalls", 0) for v in merged_by_function_data[bcfile].values()])
            bbcount = sum([v.get("bbcount", 0) for v in merged_by_function_data[bcfile].values()])
            mem_ops_count = sum([v.get("memory_ops", {}).get("total", 0) for v in merged_by_function_data[bcfile].values()])
            icall_targets = sum([v.get("FunctionCalls", {}).get("TotalIndirectCalls", 0) for v in merged_by_function_data[bcfile].values()])

            if icalls == 0:
                continue

            result[bcfile] = {
                "BasicBlocks": 0,
                "MemoryOps": 0,
                "ICalls": 0,
            }
        
        result[bcfile]["Functions"] = len(merged_by_function_data[bcfile])
        result[bcfile]["BasicBlocks"] = bbcount
        result[bcfile]["MemoryOps"] = mem_ops_count
        result[bcfile]["ICalls"] = icalls
        result[bcfile]["ICallTargets"] = icall_targets
        result[bcfile]["Ratio"] = bbcount / (icalls + icall_targets + mem_ops_count)

    return result

def merge_data_by_function(cg_data, memory_ops, bb_info):
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
                        merged[moduleName][functionName]["FunctionCalls"] = cg_data[moduleName][functionName]["FunctionCalls"]

        if not merged[moduleName]:
            del merged[moduleName]
    

    return merged

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
                    "icallTargets": 0,
                }
                if d["isIndirectCall"]:
                    cg_data[bc_filename][caller][srcline]["icall"] = True
                    cg_data[bc_filename][caller][srcline]["icallTargets"] = 1
                else:
                    cg_data[bc_filename][caller][srcline]["dcall"] = True
            else:
                cg_data[bc_filename][caller][srcline]["icallTargets"] += 1

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

    
    merged_by_function_data = merge_data_by_function(cg_data, memory_ops, bb_info)

    merged_by_function_file_data = merge_data_by_file(merged_by_function_data)
    sorted_data = dict(sorted(merged_by_function_file_data.items(), key=lambda x: x[1]['Ratio']))

    merged_by_functions_csv = "function_analysis_" + args.output + ".csv"
    merged_by_functions_json = "function_analysis_" + args.output + ".json"
    merged_by_file_csv = "file_analysis_" + args.output + ".csv"
    merged_by_file_json = "file_analysis_" + args.output + ".json"

    with open(merged_by_functions_json, "w") as f:
        json.dump(merged_by_function_data, f, indent=4)

    with open(merged_by_file_json, "w") as f:
        json.dump(sorted_data, f, indent=4)

    with open(merged_by_file_csv, "w") as f:
        f.write("File,Functions,BasicBlocks,MemoryOps,ICalls,ICallTargets,Ratio\n")
        for k, v in sorted_data.items():
            f.write(f"{k},{v['Functions']},{v['BasicBlocks']},{v['MemoryOps']},{v['ICalls']},{v['ICallTargets']},{v['Ratio']}\n")
if __name__ == "__main__":
    main()
