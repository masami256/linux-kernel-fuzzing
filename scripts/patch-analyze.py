#!/usr/bin/env python3

# install python3-unidiff if not already installed
from unidiff import PatchSet
import sys
import argparse
import re
import os
import yaml
import pprint

IS_ADDED = 0x1
IS_REMOVED = 0x2

FUNCTION_PATTERN = re.compile(
    r'^\s*(static\s+)?(\w[\w\s\*\_]*?)\s+(\w+)\s*\(([^)]*)\)\s*',
    re.MULTILINE
)
FUNCTION_PATTERN_NO_RETURN_TYPE = re.compile(
    r'^\s*(static\s+)?([\w\s\*\_]+)?\s*(\w+)\s*\(([^)]*)\)\s*',
    re.MULTILINE
)

def parse_args():
    parser = argparse.ArgumentParser(description="Analyze patch files to extract changed functions.")
    parser.add_argument("--patchfiles", help="Comma-separated list of patch files to analyze.", \
                        metavar="patchfile1,patchfile2", required=True)
    parser.add_argument("--output", help="Output file to write the results.", default="patch-analyzed-result.yml", \
                        metavar="Output file name", required=False)

    return parser.parse_args()

def get_updated_files(patch):
    updated_files = []

    for patched_file in patch:        
        updated_files.append(patched_file.path)

    return updated_files

def extract_function_name(line):

    match = FUNCTION_PATTERN.match(line)
    if match:
        function_name = match.group(3)
        return function_name

    return "OutOfFunctionScope"

def extract_function_name_no_return_type(line):

    match = FUNCTION_PATTERN_NO_RETURN_TYPE.match(line)
    if match:
        function_name = match.group(0)
        function_name = function_name.split('(')[0].split()[-1]
        return function_name

    return "OutOfFunctionScope"

def update_changed_functions(patched_file, changed_functions, key, function_names, added_lines, removed_lines):
    if not isinstance(function_names, list):
        function_names = [function_names]
    
    for function_name in function_names:
        if not function_name in changed_functions[key]:
            changed_functions[key][function_name] = {
                "file": patched_file.path,
                "added_lines": added_lines,
                "removed_lines": removed_lines
            }
        else:
            changed_functions[key][function_name]["added_lines"] += added_lines
            changed_functions[key][function_name]["removed_lines"] += removed_lines

def get_changed_functions(patch):
    """
    Get list of changed functions from the diff, ignoring function call sites.

    :param patch: The PatchSet object to analyze.
    :return: List of changed function names.
    """
    changed_functions = {
        "added": {},
        "removed": {},
        "modified": {},
    }
    
    for patched_file in patch:
        for hunk in patched_file:
            modified_type = 0
            function_is_added = False
            function_is_removed = False
            
            added_functions = []
            removed_functions = []

            section_header = hunk.section_header.strip()
            #pprint.pprint(f"section header: {section_header}")

            # Extract function name from section header.
            # Section header is of the form @@ -start_line,start_line +end_line,end_line @@.
            # Sometimes, the section header's function name is not the funciton name that is being added/removed.
            # for example, following code doesn't change fec_enet_set_coalesce().
            """
            @@ -2856,19 +2855,6 @@ static int fec_enet_set_coalesce(struct net_device *ndev,
                return 0;
            }
            
            -static void fec_enet_itr_coal_init(struct net_device *ndev)
            """

            # At first, we extract function name from section header.
            # This name might be changed if we face above case.
            function_name = extract_function_name(section_header)
            if function_name == "OutOfFunctionScope":
                function_name = extract_function_name_no_return_type(section_header)

            print(f"First function name: {function_name}")
            if not function_name == "num_online_cpus":
                pass

            print("------------------------------")
            pprint.pprint("section header: " + section_header)

            for patch_line in hunk:
                added_lines = 0
                removed_lines = 0

                line = patch_line.value.strip()
                #print(line)
                function_name_tmp = extract_function_name(line)
                if not function_name_tmp == function_name and not function_name_tmp == "OutOfFunctionScope":
                    print(f"Function name changed to: {function_name_tmp} from {function_name} check1")
                    function_name = function_name_tmp

                # If patch line is a function declaration.
                # we need to update the function name to the one extracted from the section header.
                """
                @@ -124,8 +153,9 @@ void arch_irq_work_raise(void)

                void handle_IPI(struct pt_regs *regs)
                {
                """
                if patch_line.is_added or patch_line.is_removed:
                    # If patch line is a function declaration.
                    # we need to update the function name to the one extracted from the section header.
                    match = FUNCTION_PATTERN.match(line)
                    if match:
                        # Patch line contains a function declaration.
                        # We change the function name to the one extracted from the section header.
                        function_name_tmp = extract_function_name(line) 
                        if not function_name_tmp == function_name and not function_name_tmp == "OutOfFunctionScope":
                            print(f"Function name changed to: {function_name_tmp} from {function_name_tmp} check1")
                            function_name = function_name_tmp

                        if patch_line.is_added:
                            function_is_added = True
                            added_functions.append(function_name)
                        elif patch_line.is_removed:
                            function_is_removed = True
                            removed_functions.append(function_name)

                    if patch_line.is_added:
                        modified_type |= IS_ADDED
                        added_lines += 1
                        if function_name == "num_online_cpus":
                            print(f"added line: {line}")
                    elif patch_line.is_removed:
                        modified_type |= IS_REMOVED
                        removed_lines += 1

                    if modified_type == IS_ADDED and function_is_added:
                        update_changed_functions(patched_file, changed_functions, "added", function_name, added_lines, removed_lines)
                    elif modified_type == IS_REMOVED and function_is_removed:
                        update_changed_functions(patched_file, changed_functions, "removed", function_name, added_lines, removed_lines)
                    elif modified_type & IS_ADDED or modified_type & IS_REMOVED:
                        if added_functions:
                            update_changed_functions(patched_file, changed_functions, "added", added_functions, 1, 0)
                            
                        if removed_functions:
                            update_changed_functions(patched_file, changed_functions, "removed", removed_functions, 0, 1)
                        
                        if not added_functions and not removed_functions:
                            update_changed_functions(patched_file, changed_functions, "modified", function_name, added_lines, removed_lines)
                else:
                    pass
                    #print(f"line: {line}")
                    #if added_lines == 0 and removed_lines == 0:
                    #    function_name = "OutOfFunctionScope"
            print("=====================================")
    return changed_functions

def read_patch_file(patchfile):
    with open(patchfile, 'r') as patch_file:
        return PatchSet(patch_file)

def main():
    args = parse_args()
    patchfiles = args.patchfiles.split(",")
    updated_files = {}

    for patchfile in patchfiles:
        print("Analyzing patch file: %s" % patchfile)
        patch = read_patch_file(patchfile)
        modified_functions = get_changed_functions(patch)

        modified_files = get_updated_files(patch)

        patchname = os.path.basename(patchfile)
        updated_files[patchname] = {
            "modified_files": modified_files,
            "modified_functions": modified_functions,
        }

    with open(args.output, "w") as f:
        yaml.dump(updated_files, f, default_flow_style=False)

    print(f"Analysis results written to '{args.output}'.")
if __name__ == "__main__":
    main()