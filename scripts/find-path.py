#!/usr/bin/env python3

import pickle
import sys
import networkx as nx
import argparse
import yaml

def is_syscall_function(path):
   return path.startswith("__ia32_sys_") or \
        path.startswith("__ia32_compat_sys") or \
        path.startswith("__ia32_sys_") or \
        path.startswith("__x64_sys_ia32_") or \
        path.startswith("do_syscall_64") or \
        path.startswith("__x64_sys_") or \
        path.startswith("do_int80_emulation")

def find_shortest_paths(graph, target, max_paths=20):
    """Find shortest paths leading to the target node using BFS."""
    from collections import deque

    paths = []
    queue = deque([(target, [target])])  # Queue holds (current_node, path_to_current_node)
    path_count = 0

    while queue:
        current, path = queue.popleft()

        # If we've reached a source node, add the path
        if graph.in_degree(current) == 0:
            paths.append(path)  # Keep the order as target-to-source
            path_count += 1
            if path_count >= max_paths:
                print(f"Path limit ({max_paths}) reached. Stopping exploration.")
                break

        # Add predecessors to the queue
        for predecessor in graph.predecessors(current):
            if predecessor not in path:  # Avoid cycles
                queue.append((predecessor, path + [predecessor]))

    return paths

def parse_options():
    parser = argparse.ArgumentParser()
    parser.add_argument("--picklefile", help="Pickle file path",
            metavar="PICKLEFILE", required=True)
    parser.add_argument("--func", help="target function name",
        metavar="FUNCTION", required=True)
    parser.add_argument("--output", default="paths_output.yml", help="output file path")
    parser.add_argument("--verbose", help="show all result(hide paths if they are not start from syscall)",
        action="store_true")
    
    return parser.parse_args()

def main():
    # Check if the correct number of arguments is provided
    args = parse_options()
    
    # Get the Pickle file path and target function from command-line arguments
    pickle_file_path = args.picklefile
    target_function = args.func

    try:
        # Load the graph from the Pickle file
        with open(pickle_file_path, 'rb') as f:
            call_graph = pickle.load(f)
    except Exception as e:
        print(f"Error loading Pickle file: {e}")
        sys.exit(1)

    # Check if the target function exists in the graph
    if target_function not in call_graph.nodes():
        print(f"Function '{target_function}' not found in the graph.")
        sys.exit(1)

    # Find all shortest paths to the target function
    paths = find_shortest_paths(call_graph, target_function)

    paths_arr = []

    # Display the paths
    if paths:
        print(f"Paths to '{target_function}':")
        for path in paths:
            if is_syscall_function(path[-1]) or args.verbose:
                print(" -> ".join(path[::-1]))  # Reverse the path order for display
                paths_arr.append(path[::-1])
    else:
        print(f"No paths found to '{target_function}'.")

    if len(paths_arr):
        with open(args.output, "w") as f:
            yaml.dump(paths_arr, f)

if __name__ == "__main__":
    main()
