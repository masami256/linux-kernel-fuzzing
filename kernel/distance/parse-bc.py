#!/usr/bin/env python3
import os
import re
import yaml
import subprocess
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

def extract_struct_function_pointers(ll_file_content):
    """
    Extract function pointers and types from an LLVM IR (.ll) file line by line.
    Identify structures using '@structure_name =' and extract the data inside the last {}.
    """
    struct_function_map = {}
    struct_type_map = {}
    current_struct = None
    inside_struct = False
    functions = []

    # Regular expressions to detect structure start, function pointers, and type information
    struct_start_pattern = re.compile(r'(@\w+)\s*=\s*.*%struct\.(\w+)')  # To find @struct_name = %struct.type_name
    function_pointer_pattern = re.compile(r'ptr\s+@(\w+)')  # To find ptr @function_name

    for line in ll_file_content.splitlines():
        # Check if this line starts a structure and records its type
        struct_match = struct_start_pattern.match(line)
        if struct_match:
            if current_struct and functions:
                struct_function_map[current_struct] = functions
            current_struct = struct_match.group(1)
            struct_type = struct_match.group(2)
            struct_type_map[current_struct] = struct_type  # Save the struct's type information
            functions = []
            inside_struct = True  # Now we are inside a structure

        # If inside a structure, look for function pointers
        if inside_struct:
            function_match = function_pointer_pattern.findall(line)
            if function_match:
                functions.extend(function_match)

        # Detect the end of structure (assuming it's closed by a brace '}' line)
        if inside_struct and '}' in line:
            inside_struct = False
            if current_struct and functions:
                struct_function_map[current_struct] = functions

    # Add the last structure and its functions to the map
    if current_struct and functions:
        struct_function_map[current_struct] = functions

    return struct_function_map, struct_type_map

def extract_function_definitions(ll_file_content):
    """
    Extract function definitions from an LLVM IR (.ll) file.
    """
    function_definitions = re.findall(r'define.*?@(\w+)\s*\(', ll_file_content)
    return function_definitions

def analyze_ll_file(ll_file):
    """
    Analyze a single .ll file and extract function pointer assignments, function definitions, and structure types.
    Return a dictionary of results for the .ll file.
    """
    with open(ll_file, 'r') as f:
        ll_file_content = f.read()

    # Extract struct function pointers and types
    struct_function_map, struct_type_map = extract_struct_function_pointers(ll_file_content)
    
    # Extract function definitions
    function_definitions = extract_function_definitions(ll_file_content)
    
    return {"struct_function_map": struct_function_map, "struct_type_map": struct_type_map, "function_definitions": function_definitions}

def bc_to_ll(bc_file, llvm_bin_dir):
    """
    Convert a .bc file to .ll using llvm-dis and save it in the same directory as the .bc file.
    """
    ll_file = bc_file.replace('.bc', '.ll')
    print(f"Run llvm-dis for {bc_file}")
    subprocess.run([f"{llvm_bin_dir}/llvm-dis", bc_file, '-o', ll_file], check=True)
    return ll_file

def process_bc_file(bc_file, llvm_bin_dir):
    """
    Process a .bc file: convert to .ll and analyze the resulting .ll file.
    """
    try:
        ll_file = bc_to_ll(bc_file, llvm_bin_dir)
        struct_function_map = analyze_ll_file(ll_file)
        return bc_file, struct_function_map
    except Exception as e:
        return bc_file, {}

def analyze_bc_files_recursively(bc_directory, max_workers, llvm_bin_dir):
    """
    Recursively analyze all .bc files in a directory, converting them to .ll files,
    and then extracting function pointer assignments using a thread pool for parallel processing.
    """
    all_results = {}
    bc_files = []

    # Recursively find all .bc files in the directory
    for root, _, files in os.walk(bc_directory):
        for file in files:
            if file.endswith('.bc'):
                bc_files.append(os.path.join(root, file))

    # Use ThreadPoolExecutor to parallelize the process
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_bc_file, bc_file, llvm_bin_dir): bc_file for bc_file in bc_files}

        for future in as_completed(futures):
            bc_file, result = future.result()
            all_results[bc_file] = result

    return all_results

def save_to_yaml(data, yaml_file):
    """Save the extracted function pointers, structure types, and function definitions to a YAML file."""
    with open(yaml_file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Recursively analyze .bc files, convert them to .ll files, and extract function pointers, structure types, and functions.")
    parser.add_argument('-b', '--bc_directory', type=str, required=True, help="Directory containing .bc files to be analyzed")
    parser.add_argument('-o', '--output_yaml', type=str, default='ll_parsed.yml', help="Output YAML file to store the extracted data")
    parser.add_argument('-t', '--threads', type=int, default=4, help="Number of parallel threads to use for processing")
    parser.add_argument('--llvm-bin-dir', required=True, help="PATH to llvm binaries directory")

    args = parser.parse_args()

    # Analyze all .bc files recursively in the given directory with specified number of threads
    all_results = analyze_bc_files_recursively(args.bc_directory, args.threads, args.llvm_bin_dir)

    # Save the results to a YAML file
    save_to_yaml(all_results, args.output_yaml)
    print(f"[INFO] Results saved to {args.output_yaml}")

if __name__ == "__main__":
    main()
