import pickle
import sys
import networkx as nx
from collections import deque

def find_all_paths(graph, start, max_paths=20):
    """
    Finds all paths from the start node to leaf nodes in a directed graph.

    Args:
        graph: A NetworkX directed graph.
        start: The starting node for the search.
        max_paths: The maximum number of paths to find.

    Returns:
        A list of paths, where each path is a list of nodes.
    """

    paths = []
    queue = deque([(start, [start])])
    path_count = 0

    while queue:
        current, path = queue.popleft()

        # If the current node has no outgoing edges, it's a leaf node.
        if graph.out_degree(current) == 0:
            paths.append(path)
            path_count += 1
            if path_count >= max_paths:
                print(f"Path limit ({max_paths}) reached. Stopping exploration.")
                break

        # Explore the successors of the current node.
        for successor in graph.successors(current):
            if successor not in path:  # Avoid cycles
                queue.append((successor, path + [successor]))

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

    # Find all paths from the target function to leaf nodes
    paths = find_all_paths(call_graph, target_function)

    # Display the paths
    if paths:
        print(f"Paths from '{target_function}':")
        for path in paths:
            print(" -> ".join(path))
    else:
        print(f"No paths found from '{target_function}'.")

if __name__ == "__main__":
    main()