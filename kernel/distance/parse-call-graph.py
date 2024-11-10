#!/usr/bin/env python3

import yaml
import os
import networkx as nx
import argparse
import pickle
import re

def load_yaml(yaml_file):
    """Load struct-function mapping from a YAML file."""
    with open(yaml_file, 'r') as f:
        return yaml.safe_load(f)

def extract_braced_text(s):
    """Extract text enclosed in braces."""
    if not s:
        return None
    match = re.search(r'\{(.*?)\}', s)
    return match.group(1) if match else None

def load_graph_from_pickle(pickle_file):
    """Load a graph from a Pickle file."""
    with open(pickle_file, 'rb') as f:
        return pickle.load(f)

def build_label_to_node_map(graph):
    """Build a dictionary mapping function names (from labels) to node IDs."""
    label_to_node = {}
    for node, data in graph.nodes(data=True):
        label = extract_braced_text(data.get("label"))
        if label:
            label_to_node[label] = node
    return label_to_node

def extract_function_pointer_calls(block_label):
    if "ext4_file_operations" in block_label:
        print(f"[DEBUG] ext4_file_operations detected in CFG node {cfg_node}")

    """
    Extract potential function pointer calls from a block label.
    Includes both direct member access (->) and getelementptr instructions for file_operations open calls.
    """
    # Adjust pattern to include flexible field indexing for getelementptr instructions
    function_pointer_call_pattern = re.compile(
        r'(\w+)->(\w+)\s*\(|%(\w+)\s*=\s*getelementptr\s+inbounds\s+%struct\.(\w+), ptr\s+%\w+, (?:i32|i64)\s+\d+, i32\s+(\d+)'
    )
    matches = function_pointer_call_pattern.findall(block_label)

    calls = []
    for match in matches:
        if match[0] and match[1]:  # Direct struct access like "f_op->open()"
            calls.append((match[0], match[1]))
        elif match[2] and match[3] and match[4]:  # GEP (getelementptr) with flexible field index
            struct_name = match[3]
            field_index = int(match[4])
            if struct_name == "file_operations" and field_index == 0:  # Check for open at index 0
                calls.append((struct_name, "open"))

    if calls:
        print(f"[DEBUG] Function pointer calls detected: {calls}")
    return calls

def dynamically_build_struct_function_map(call_graph, cfg_graph, struct_function_map):
    """
    Track the use of struct file_operations and resolve function pointer calls.
    """
    call_label_to_node = build_label_to_node_map(call_graph)
    stored_variables = {}

    for cfg_node, cfg_data in cfg_graph.nodes(data=True):
        block_label = cfg_data.get("label", "")
        print(f"[DEBUG] Processing CFG node {cfg_node} with label: {block_label}")

        # Detect store operations related to struct file_operations
        store_match = re.search(r'store ptr @(\w+), ptr %(\w+)', block_label)
        if store_match:
            struct_name, var_name = store_match.groups()
            if struct_name == "ext4_file_operations":
                stored_variables[var_name] = "ext4_file_operations"
                print(f"[DEBUG] Detected store to ext4_file_operations in variable %{var_name}")

        # Check if stored variables are used in subsequent function calls
        for var_name, struct_name in stored_variables.items():
            if var_name in block_label:
                print(f"[DEBUG] Variable %{var_name} (ext4_file_operations) used in: {block_label}")

                # Detect GEP or load operations on the stored variable
                if "getelementptr" in block_label or "load" in block_label:
                    print(f"[DEBUG] Detected getelementptr or load using variable %{var_name} in block: {block_label}")

                    # Extract function pointer calls from the block label
                    calls = extract_function_pointer_calls(block_label)
                    if calls:
                        print(f"[DEBUG] Function pointer calls detected: {calls}")

                        # Resolve the function pointer to the actual function
                        for struct_name, func_ptr_name in calls:
                            if struct_name in struct_function_map:
                                real_function = struct_function_map[struct_name].get(func_ptr_name)
                                if real_function:
                                    print(f"[DEBUG] Resolved function pointer {func_ptr_name} to function {real_function}")
                                    if real_function in call_label_to_node:
                                        target_node = call_label_to_node[real_function]
                                        print(f"[DEBUG] Adding edge from CFG node {cfg_node} to CG node {target_node} ({real_function})")
                                        call_graph.add_edge(cfg_node, target_node)
                                    else:
                                        print(f"[WARNING] Function {real_function} not found in call graph.")
                                else:
                                    print(f"[WARNING] Could not resolve function pointer {func_ptr_name} in struct {struct_name}")
                    else:
                        print(f"[DEBUG] No function pointer calls found in block {block_label}")

def integrate_cfg_with_graph(call_graph, cfg_graph, target_function, struct_function_map):
    """
    Integrate the CFG graph information into the call graph by matching the function name.
    Also handles struct-based function pointers, including static initializations from YAML.
    """
    dynamically_build_struct_function_map(call_graph, cfg_graph, struct_function_map)

    # Build a map from function labels to nodes in the call graph
    call_label_to_node = build_label_to_node_map(call_graph)
    node_to_function_label = {v: k for k, v in call_label_to_node.items()}  # Reverse mapping from NodeID to FunctionName

    # Find the corresponding node in the call graph by the function name
    if target_function in call_label_to_node:
        call_graph_node = call_label_to_node[target_function]
        print(f"[DEBUG] Found corresponding call graph node for function {target_function}: {call_graph_node}")

        # Explore all paths to the target function from any node in the graph
        paths_to_function = []
        for source_node in call_graph.nodes():
            if source_node != call_graph_node:
                try:
                    paths = list(nx.all_simple_paths(call_graph, source=source_node, target=call_graph_node))
                    paths_to_function.extend(paths)
                except nx.NetworkXNoPath:
                    continue

        # Print all the paths to the target function with NodeID and FunctionName
        if paths_to_function:
            print(f"All paths to {target_function}:")
            for path in paths_to_function:
                path_with_functions = []
                for node in path:
                    fn_name = node_to_function_label.get(node, "Unknown")
                    path_with_functions.append(f"{node}({fn_name})")
                print(" -> ".join(path_with_functions))
        else:
            print(f"No paths found to {target_function}.")
    else:
        print(f"[ERROR] Function {target_function} not found in the call graph.")

def main():
    # Use argparse to process command-line arguments
    parser = argparse.ArgumentParser(description="Find all call paths to a specific function in a graph, considering function pointers.")
    parser.add_argument('--cg', type=str, required=True, help="Path to the Pickle file containing the call graph")
    parser.add_argument('--function', type=str, required=True, help="Target function to find paths to")
    parser.add_argument('--cfg', type=str, required=True, help="Path to the Pickle CFG file for function pointers")
    parser.add_argument('--yaml', type=str, required=True, help="YAML file with struct-function pointer mappings")

    args = parser.parse_args()

    cg_file = args.cg
    target_function = args.function
    cfg_file = args.cfg
    yaml_file = args.yaml

    # Load struct-function mappings from YAML
    struct_function_map = load_yaml(yaml_file)

    # Check if the Pickle file exists
    if not os.path.isfile(cg_file):
        print(f"Invalid file: {cg_file}")
        return

    # Load the call graph from the Pickle file
    call_graph = load_graph_from_pickle(cg_file)

    # Load the control flow graph from the Pickle file
    cfg_graph = load_graph_from_pickle(cfg_file)

    # Integrate CFG with the call graph and print the paths to the target function
    integrate_cfg_with_graph(call_graph, cfg_graph, target_function, struct_function_map)

if __name__ == "__main__":
    main()
