#!/usr/bin/env python3

import networkx as nx
import matplotlib.pyplot as plt
import json
import sys
import glob
import os
import pickle

def save_graph(graph, output_path_pickle):
    """Save the graph in Pickle format."""
    try:
        # Save as Pickle
        with open(output_path_pickle, 'wb') as f:
            pickle.dump(graph, f)
        print(f"Graph saved as Pickle: {output_path_pickle}")

    except Exception as e:
        print(f"Error saving the graph: {e}")

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <bcfiles directory> <output_directory>")
        sys.exit(1)
    
    directory_path = sys.argv[1]
    output_directory = sys.argv[2]

    if not os.path.isdir(directory_path):
        print(f"Error: {directory_path} is not a valid directory.")
        sys.exit(1)

    if not os.path.isdir(output_directory):
        print(f"Error: {output_directory} is not a valid directory.")
        sys.exit(1)

    # Find all JSON files in the directory and its subdirectories
    json_files = glob.glob(os.path.join(directory_path, '**', 'callgraph-*.json'), recursive=True)

    if not json_files:
        print(f"No JSON files found in the directory: {directory_path}")
        sys.exit(1)

    # Create a unified directed graph
    unified_call_graph = nx.DiGraph()

    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                call_data = json.load(f)
            for caller, callee in call_data:
                unified_call_graph.add_edge(caller, callee)
        except Exception as e:
            print(f"Error processing file {json_file}: {e}")

    # Output graph information
    #print(f"Nodes: {unified_call_graph.nodes()}")
    #print(f"Edges: {unified_call_graph.edges()}")

    # Save the graph in Pickle format
    output_path_pickle = os.path.join(output_directory, "unified_call_graph.pkl")
    save_graph(unified_call_graph, output_path_pickle)

    # Visualize the unified graph
    # plt.figure(figsize=(12, 8))
    # pos = nx.spring_layout(unified_call_graph)
    # nx.draw(
    #     unified_call_graph, pos, with_labels=True, 
    #     node_size=2000, node_color="lightblue", 
    #     font_size=10, font_weight="bold", arrowsize=20
    # )
    # plt.title("Unified Call Graph")
    # plt.show()

if __name__ == "__main__":
    main()