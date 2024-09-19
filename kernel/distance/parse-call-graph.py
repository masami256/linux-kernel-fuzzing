#!/usr/bin/env python3
import os
import networkx as nx
import argparse
import pickle
import pprint
import re

def extract_braced_text(s):
    if not s:
        return None
    
    match = re.search(r'\{(.*?)\}', s)
    if match:
        return match.group(1)  
    return None

def load_graph_from_pickle(pickle_file):
    """
    Load a graph from a Pickle file.
    """
    with open(pickle_file, 'rb') as f:
        return pickle.load(f)

def find_all_paths_to_function2(G, target_function):
    """
    Find all paths that lead to the target function in the call graph.
    """
    # Find the node corresponding to the target function
    target_node = None
    for node, data in G.nodes(data=True):
        if extract_braced_text(data.get("label")) == target_function:
            target_node = node
            break

    if target_node is None:
        print(f"Function {target_function} not found in the graph.")
        return []

    # Now find all paths to the target_node
    paths = []
    for node in G.nodes():
        if node != target_node:
            # Find all simple paths from `node` to `target_node`
            for path in nx.all_simple_paths(G, source=node, target=target_node):
                paths.append(path)
    return paths

def find_all_paths_to_function(G, target_function):
    """
    Find all paths that lead to the target function in the call graph.
    Each path is a list of tuples: (node ID, function name).
    """
    # Find the node corresponding to the target function
    target_node = None
    for node, data in G.nodes(data=True):
        if extract_braced_text(data.get("label")) == target_function:
            target_node = node
            break

    if target_node is None:
        print(f"Function {target_function} not found in the graph.")
        return []

    paths = []
    for node in G.nodes():
        if node != target_node:
            # Find all simple paths from `node` to `target_node`
            for path in nx.all_simple_paths(G, source=node, target=target_node):
                # Create a list of (node ID, function name) tuples for each path
                labeled_path = [(n, extract_braced_text(G.nodes[n].get('label', n))) for n in path]
                paths.append(labeled_path)
    return paths


def main():
    # Use argparse to process command-line arguments
    parser = argparse.ArgumentParser(description="Find all call paths to a specific function in a graph")
    parser.add_argument('-p', '--pickle', type=str, required=True, help="Path to the Pickle file containing the graph")
    parser.add_argument('-f', '--function', type=str, required=True, help="Target function to find paths to")
    
    args = parser.parse_args()

    pickle_file = args.pickle
    target_function = args.function

    # Check if the Pickle file exists
    if not os.path.isfile(pickle_file):
        print(f"Invalid file: {pickle_file}")
        return

    # Load the graph from the Pickle file
    call_graph = load_graph_from_pickle(pickle_file)

    # Find all paths to the target function
    paths_to_function = find_all_paths_to_function(call_graph, target_function)

    # Print all the paths to the target function
    if paths_to_function:
        print(f"All paths to {target_function}:")
        for path in paths_to_function:
            print(" -> ".join([f"{n}({fn})" for n, fn in path]))

    else:
        print(f"No paths found to {target_function}")

if __name__ == "__main__":
    main()
