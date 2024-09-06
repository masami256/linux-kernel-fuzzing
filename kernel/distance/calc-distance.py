#!/usr/bin/env python3
import networkx as nx
import math
import sys
import os

def load_graph_from_dot(dot_file_path):
    """
    Load a networkx multigraph from an LLVM .dot file and set edge weights
    """
    # Load the .dot file
    G = nx.drawing.nx_agraph.read_dot(dot_file_path)
    
    # Dictionary to store edge weights
    edge_weights = {}

    # Extract Probability from the tooltip of edges and set as edge weight
    for u, v, k, data in G.edges(keys=True, data=True):  # Supports multigraphs
        tooltip = data.get('tooltip', '')
        
        # Extract Probability information
        probability_str = tooltip.split('Probability ')[-1].strip('%').strip() if 'Probability' in tooltip else None
        if probability_str is not None:
            probability = float(probability_str) / 100.0  # e.g. 62.50% -> 0.625
            # Ensure probability is in the valid range (0 < probability <= 1)
            if probability > 0:
                # Calculate weight using the negative logarithm (higher probability = shorter distance)
                edge_weights[(u, v, k)] = -math.log2(probability)
            else:
                # Set a large default weight if the probability is zero or negative
                edge_weights[(u, v, k)] = float('inf')  # Infinite distance
        else:
            # Set a default weight if no probability is found
            edge_weights[(u, v, k)] = 1.0
    
    # Use set_edge_attributes to assign weights to edges in bulk
    nx.set_edge_attributes(G, edge_weights, 'weight')
    
    return G

def calculate_all_pair_distances(dot_file_path, output_filename):
    """
    Load an LLVM .dot file and compute the shortest distances between all nodes
    """
    # Load the graph
    G = load_graph_from_dot(dot_file_path)
    
    # Compute the shortest path between all nodes
    all_distances = dict(nx.shortest_path_length(G, weight='weight'))
    
    # Output the distances between all node pairs
    with open(output_filename, "w") as f:
        for source, target_distances in all_distances.items():
            for target, distance in target_distances.items():
                f.write(f"Distance from {source} to {target}: {distance}\n")

if __name__ == "__main__":
    if not len(sys.argv) == 2:
        print(f"[*]Usage {sys.argv[0]} <dot file>")
        exit(1)
    
    dotfile = sys.argv[1]
    basename = os.path.basename(dotfile)
    d = os.path.realpath(os.path.dirname(dotfile))

    output_filename = f"{d}/distance-{basename}"
    # Calculate shortest distances between all node pairs
    calculate_all_pair_distances(dotfile, output_filename)
