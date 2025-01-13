#!/usr/bin/env python3

import sys
import glob
import os
import json
import re

import pprint

MEMORY_OPERATIONS = [
    "__kmalloc",
    "kmalloc_large",
    "kmalloc",
    "kzalloc",
    "kcalloc",
    "kfree",
]

def main(directory_path):
    if not os.path.isdir(directory_path):
        print(f"Error: {directory_path} is not a valid directory.")
        sys.exit(1)

    restr = r"-(.*?)[.]"
    paths = directory_path.split("/")
    idx = paths.index("bcfiles") + 1
    paths = "/".join(paths[idx:])

    all_data = {}

    json_files = glob.glob(os.path.join(directory_path, '**', 'callgraph-*.json'), recursive=True)
    for j in json_files:
        tmp = j.split("/")
        paths = "/".join(tmp[idx:len(tmp) -1])
        c_filename = paths + "/" + re.search(restr, os.path.basename(j)).group(1) + ".c"
        
        all_data[c_filename] = {}

        with open(j) as f:
            data = json.load(f)

        for funcs in data:
            caller = funcs[0]
            callee = funcs[1]

            if callee in MEMORY_OPERATIONS:
                if not caller in all_data[c_filename]:
                    all_data[c_filename][caller] = [callee]
                else:
                    all_data[c_filename][caller].append(callee)

        # remove empty data
        if not all_data[c_filename]:
            del all_data[c_filename]
        
    with open("memory_ops.csv", "w") as f:
        f.write("source file, caller, callee\n")
        for filename in all_data:
            for funcname in all_data[filename]:
                for callee in all_data[filename][funcname]:
                    f.write(f"{filename}, {funcname}, {callee}\n")

    print("[+]Parse result was written to memory_ops.csv")
    
if __name__ == "__main__":
    if not len(sys.argv) == 2:
        print(f"[*]Usage {sys.argv[0]} <path to callgraph json file director")
        exit(1)

    main(sys.argv[1])