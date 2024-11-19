#!/usr/bin/env python3

import pickle
import sys
import networkx as nx

def find_paths_memory_optimized(graph, target, max_paths=20):
    """Find all paths leading to the target node with a path limit."""
    paths = []
    stack = [(target, None)]  # Stack holds (current_node, parent_node)
    parent_map = {}  # To reconstruct paths later
    path_count = 0  # Counter for paths found

    while stack:
        current, parent = stack.pop()
        if current not in parent_map:
            parent_map[current] = parent  # Record the parent node

            # Add predecessors to the stack, sorted by in-degree (optional priority)
            for predecessor in sorted(graph.predecessors(current), key=lambda x: graph.in_degree(x)):
                stack.append((predecessor, current))

    # Reconstruct paths from the parent map
    def reconstruct_path(node):
        path = []
        while node is not None:
            path.append(node)
            node = parent_map[node]
        return path[::-1]  # Reverse the path

    for node in parent_map:
        if graph.in_degree(node) == 0:  # Source node
            paths.append(reconstruct_path(node))
            path_count += 1
            if path_count >= max_paths:
                print(f"Path limit ({max_paths}) reached. Stopping exploration.")
                return paths

    return paths

def main():
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 3:
        print("Usage: python script.py <path_to_pickle_file> <target_function>")
        sys.exit(1)
    
    # Get the Pickle file path and target function from command-line arguments
    pickle_file_path = sys.argv[1]
    target_function = sys.argv[2]

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

    # Find all paths to the target function
    paths = find_paths_memory_optimized(call_graph, target_function)

    # Display the paths
    if paths:
        print(f"Paths to '{target_function}':")
        for path in paths:
            print(" -> ".join(path[::-1]))  # Reverse the path order for display
    else:
        print(f"No paths found to '{target_function}'.")


if __name__ == "__main__":
    main()
