#!/usr/bin/env python3

import json
import argparse
import glob
import os
import sys
import pprint

def parse_options():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", help="Path to callgraph json file director",
        metavar="DIRECTORY", required=True)

    args = parser.parse_args()
    if not args.dir:
        print("[*]You must provide a directory path")
        sys.exit(1)
    
    return args

def main():
    args = parse_options()

    all_data = {}

    json_files = glob.glob(os.path.join(args.dir, '**', 'callgraph-*.json'), recursive=True)
    for jf in json_files:
        with open(jf) as f:
            data = json.load(f)
            for d in data:
                moduleName = d["ModuleName"]
                if moduleName not in all_data:
                    all_data[moduleName] = {}
                
                caller = d["CallerName"]

                if not caller in all_data[moduleName]:
                    all_data[moduleName][caller] = {
                        "icalls": 0,
                        "dcalls": 0,
                    }

                if d["isIndirectCall"]:
                    all_data[moduleName][caller]["icalls"] += 1
                else:
                    all_data[moduleName][caller]["dcalls"] += 1

    pprint.pprint(all_data)
    
if __name__ == "__main__":
    main()