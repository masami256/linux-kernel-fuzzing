#!/usr/bin/env python3

# install python3-unidiff if not already installed
from unidiff import PatchSet
import sys
import argparse
import re
import pprint

IS_ADDED = 0x1
IS_REMOVED = 0x2

FUNCTION_PATTERN = re.compile(
    r'^\s*(static\s+)?(\w[\w\s\*]*?)\s+(\w+)\s*\(([^)]*)\)\s*',
    re.MULTILINE
)

def parse_args():
    parser = argparse.ArgumentParser(description="Analyze patch files to extract changed functions.")
    parser.add_argument("--patchfiles", help="Comma-separated list of patch files to analyze.", \
                        metavar="patchfile1,patchfile2", required=True)
    return parser.parse_args()

def get_updated_files(patch):
    updated_files = []

    for patched_file in patch:        
        updated_files.append(patched_file.path)

    return updated_files

def extract_function_name(line):

    function_declaration = line.strip().split('(')[0]
    if len(function_declaration) == 0:
        return None

    function_name = function_declaration.split(' ')[-1]
    return function_name

def update_changed_functions(changed_functions, key, function_name):
    if not function_name in changed_functions[key]:
        changed_functions[key][function_name] = {}

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

            tmp_added_function = None
            tmp_removed_function = None

            section_header = hunk.section_header.strip()
            pprint.pprint(f"section header: {section_header}")

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

            for patch_line in hunk:
                modified_lines = 0
                added_lines = 0
                removed_lines = 0

                line = patch_line.value.strip()
                if patch_line.is_added or patch_line.is_removed:
                    match = FUNCTION_PATTERN.match(line)
                    if match:
                        # Patch line contains a function declaration.
                        # We change the function name to the one extracted from the section header.
                        function_name = line.split('(')[0].split()[-1]
                        if patch_line.is_added:
                            function_is_added = True
                            added_lines += 1
                            tmp_added_function = function_name
                        elif patch_line.is_removed:
                            function_is_removed = True
                            removed_lines += 1
                            tmp_removed_function = function_name  
                        elif patch_line.is_modified:
                            modified_lines += 1

                if patch_line.is_added:
                    modified_type |= IS_ADDED
                elif patch_line.is_removed:
                    modified_type |= IS_REMOVED

            print(f"function_name: {function_name}, modified_type: {modified_type}, function_is_added: {function_is_added}, function_is_removed: {function_is_removed}")
            if modified_type == IS_ADDED and function_is_added:
                update_changed_functions(changed_functions, "added", function_name)
            elif modified_type == IS_REMOVED and function_is_removed:
                update_changed_functions(changed_functions, "removed", function_name)
            elif modified_type & IS_ADDED or modified_type & IS_REMOVED:
                if tmp_added_function:
                    update_changed_functions(changed_functions, "added", tmp_added_function)
                    
                if tmp_removed_function:
                    update_changed_functions(changed_functions, "removed", tmp_removed_function)
                
                if tmp_added_function is None and tmp_removed_function is None:
                    update_changed_functions(changed_functions, "modified", function_name)

    for removed in changed_functions["removed"]:
        if removed in changed_functions["modified"]:
            del changed_functions["modified"][removed]

    return changed_functions



def read_patch_file(patchfile):
    with open(patchfile, 'r') as patch_file:
        return PatchSet(patch_file)

def main():
    args = parse_args()
    patchfiles = args.patchfiles.split(",")

    for patchfile in patchfiles:
        print("Analyzing patch file: %s" % patchfile)
        patch = read_patch_file(patchfile)
        modified_functions = get_changed_functions(patch)
        updated_files = get_updated_files(patch)
        pprint.pprint(updated_files)
        pprint.pprint(modified_functions)

if __name__ == "__main__":
    main()