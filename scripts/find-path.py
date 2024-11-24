#!/usr/bin/env python3

import pickle
import sys
import networkx as nx

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

    # Find all shortest paths to the target function
    paths = find_shortest_paths(call_graph, target_function)

    # Display the paths
    if paths:
        print(f"Paths to '{target_function}':")
        for path in paths:
            print(" -> ".join(path[::-1]))  # Reverse the path order for display
    else:
        print(f"No paths found to '{target_function}'.")


if __name__ == "__main__":
    main()
