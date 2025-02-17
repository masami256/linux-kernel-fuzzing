#!/usr/bin/env python3

import pickle
import sys
import networkx as nx
import argparse
import yaml
from collections import deque

def is_syscall_function(path):
    return any(path.startswith(prefix) for prefix in [
        "__ia32_sys_", "__ia32_compat_sys", "__ia32_sys_",
        "__x64_sys_ia32_", "do_syscall_64", "__x64_sys_", 
        "do_int80_emulation"
    ])

def find_shortest_paths(graph, target, max_paths=20):
    """Find shortest paths leading to the target node using BFS."""
    paths = []
    queue = deque([(target, [target])])  # Queue holds (current_node, path_to_current_node)
    path_count = 0

    while queue and path_count < max_paths:
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
    parser = argparse.ArgumentParser(description="Find paths in a call graph.")
    parser.add_argument("--picklefile", help="Pickle file path", metavar="PICKLEFILE", required=True)
    parser.add_argument("--func", help="Target function name", metavar="FUNCTION", required=True)
    parser.add_argument("--output", default="paths_output.yml", help="Output file path")
    parser.add_argument("--verbose", help="Show all results (including non-syscall paths)", action="store_true")
    
    return parser.parse_args()

def load_graph_from_pickle(pickle_file_path):
    try:
        with open(pickle_file_path, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        print(f"Error loading Pickle file: {e}")
        sys.exit(1)

def main():
    args = parse_options()
    
    call_graph = load_graph_from_pickle(args.picklefile)
    
    if args.func not in call_graph.nodes:
        print(f"Function '{args.func}' not found in the graph.")
        sys.exit(1)

    paths = find_shortest_paths(call_graph, args.func)
    
    if paths:
        print(f"Paths to '{args.func}':")
        paths_arr = [path[::-1] for path in paths if is_syscall_function(path[-1]) or args.verbose]
        for path in paths_arr:
            print(" -> ".join(path))
        
        with open(args.output, "w") as f:
            yaml.dump(paths_arr, f)
    else:
        print(f"No paths found to '{args.func}'.")

if __name__ == "__main__":
    main()