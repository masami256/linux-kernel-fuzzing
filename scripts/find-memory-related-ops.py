#!/usr/bin/env python3

import sys
import glob
import os
import json
import re
import argparse

import pprint

KERNEL_MEMORY_ALLOC_OPERATIONS = [
    "__kmalloc",
    "kmalloc_large",
    "kmalloc",
    "kzalloc",
    "kcalloc",
    "kfree"
]

LIBC_MEMORY_ALLOC_OPERATIONS = [
    "malloc",
    "calloc",
    "realloc",
    "free"
]

MEMORY_OPERATIONS = None

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

        for d in data:
            caller = d["CallerName"]
            callee = d["CalleeName"]

            if callee in MEMORY_OPERATIONS:
                if not caller in all_data[c_filename]:
                    all_data[c_filename][caller] = [callee]
                else:
                    all_data[c_filename][caller].append(callee)

        # remove empty data
        if not all_data[c_filename]:
            del all_data[c_filename]
    
    with open("memory_ops.json", "w") as f:
        json.dump(all_data, f, indent=4)

    with open("memory_ops.csv", "w") as f:
        f.write("source file, caller, callee\n")
        for filename in all_data:
            for funcname in all_data[filename]:
                for callee in all_data[filename][funcname]:
                    f.write(f"{filename}, {funcname}, {callee}\n")

    print("[+]Parse result was written to memory_ops.csv")

def parse_options():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kmalloc", help="check kmalloc related operations", action="store_true")
    parser.add_argument("--malloc", help="check malloc related operations", action="store_true")
    parser.add_argument("--dir", help="Path to callgraph json file director",
        metavar="DIRECTORY", required=True)
    
    args = parser.parse_args()
    if args.kmalloc and args.malloc:
        print("[-]You can only choose one of kmalloc or malloc")
        sys.exit(1)
    
    return args

if __name__ == "__main__":

    args = parse_options()
    if args.kmalloc:
        MEMORY_OPERATIONS = KERNEL_MEMORY_ALLOC_OPERATIONS
    elif args.malloc:
        MEMORY_OPERATIONS = LIBC_MEMORY_ALLOC_OPERATIONS

    main(args.dir)