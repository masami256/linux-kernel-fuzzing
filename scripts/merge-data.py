#!/usr/bin/env python3

import argparse
import sys
import os
import glob
import json
import re

import pprint


def merge_data_by_file(merged_by_function_data):
    tmp = {} 
    result = []

    for bcfile in merged_by_function_data:
        if not bcfile in tmp:
            icalls = sum([v.get("FunctionCalls", {}).get("TotalIndirectCalls", 0) for v in merged_by_function_data[bcfile].values()])
            bbcount = sum([v.get("bbcount", 0) for v in merged_by_function_data[bcfile].values()])
            icall_targets = sum([v.get("FunctionCalls", {}).get("TotalIndirectCallTargets", 0) for v in merged_by_function_data[bcfile].values()])

            if icalls == 0:
                continue

            tmp[bcfile] = {
                "BasicBlocks": 0,
                "ICalls": 0,
            }
        
        tmp[bcfile]["BCFile"] = bcfile
        tmp[bcfile]["Functions"] = len(merged_by_function_data[bcfile])
        tmp[bcfile]["BasicBlocks"] = bbcount
        tmp[bcfile]["ICalls"] = icalls
        tmp[bcfile]["ICallTargets"] = icall_targets

        result.append(tmp[bcfile])

    return sorted(result, key=lambda x: (-x["BasicBlocks"], -x["ICallTargets"]))

def merge_data_by_function(cg_data, bb_info):
    merged = {}

    for moduleName in cg_data:
        merged[moduleName] = {}
        if moduleName in bb_info:
            for functionName in cg_data[moduleName]:
                if functionName.startswith("lkf_source_line_"):
                    continue
                merged[moduleName][functionName] = {}
                merged[moduleName][functionName]["bbcount"] = bb_info[moduleName][functionName]["BasicBlocks"]
                merged[moduleName][functionName]["FunctionCalls"] = cg_data[moduleName][functionName]["FunctionCalls"]

        if not merged[moduleName]:
            del merged[moduleName]
    

    return merged

def read_bb_info_json(bb_info_json):
    with open(bb_info_json) as f:
        bb_info = json.load(f)
    return bb_info

def count_function_calls(cg_data):
    for bc_filename in cg_data:
        for caller in cg_data[bc_filename]:
            for sl in cg_data[bc_filename][caller]:
                if sl.startswith("lkf_source_line_"):
                    if cg_data[bc_filename][caller][sl]["icall"]:
                        cg_data[bc_filename][caller]["FunctionCalls"]["TotalIndirectCalls"] += 1
                        cg_data[bc_filename][caller]["FunctionCalls"]["TotalIndirectCallTargets"] += cg_data[bc_filename][caller][sl]["icallTargets"]

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
                        "TotalIndirectCallTargets": 0,
                    },
                }
            
            line_str = "lkf_source_line_" + str(srcline)
            if not line_str in cg_data[bc_filename][caller]:
                cg_data[bc_filename][caller][line_str] = {
                    "icall": False,
                    "dcall": False,
                    "icallTargets": 0,
                }
                if d["isIndirectCall"]:
                    cg_data[bc_filename][caller][line_str]["icall"] = True
                    cg_data[bc_filename][caller][line_str]["icallTargets"] = 1
                else:
                    cg_data[bc_filename][caller][line_str]["dcall"] = True
            else:
                cg_data[bc_filename][caller][line_str]["icallTargets"] += 1

    return count_function_calls(cg_data)


def parse_options():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bcfiles-dir", help="path to bcfiles", required=True,
                        metavar="BCFILES_DIR")
    parser.add_argument("--bb-info-json", help="BasicBlock information json", required=True,
                        metavar="BB_INFO_JSON")  
    parser.add_argument("--output", help="Output file name", required=False,
                        metavar="OUTPUT_FILE_NAME", default="output")  
    args = parser.parse_args()
    return args

def main():
    args = parse_options()
    
    cg_data = read_callgraph_json(args.bcfiles_dir)
    with open("cg_data.json", "w") as f:
        json.dump(cg_data, f, indent=4)

    merged_by_functions_csv = "function_analysis_" + args.output + ".csv"
    bb_info = read_bb_info_json(args.bb_info_json)

    merged_by_function_data = merge_data_by_function(cg_data, bb_info)

    merged_by_function_file_data = merge_data_by_file(merged_by_function_data)

    merged_by_functions_csv = "function_analysis_" + args.output + ".csv"
    merged_by_functions_json = "function_analysis_" + args.output + ".json"
    merged_by_file_csv = "file_analysis_" + args.output + ".csv"
    merged_by_file_json = "file_analysis_" + args.output + ".json"

    with open(merged_by_functions_json, "w") as f:
        json.dump(merged_by_function_data, f, indent=4)

    with open(merged_by_file_json, "w") as f:
        json.dump(merged_by_function_file_data, f, indent=4)

    with open(merged_by_file_csv, "w") as f:
        f.write("File,Functions,BasicBlocks,ICalls,ICallTargets\n")
        for v in merged_by_function_file_data:
            f.write(f"{v['BCFile']},{v['Functions']},{v['BasicBlocks']},{v['ICalls']},{v['ICallTargets']}\n")
    
    print(f"Output written to {merged_by_file_csv} and {merged_by_file_json}")

if __name__ == "__main__":
    main()
