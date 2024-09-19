#!/usr/bin/env python3

import os
import networkx as nx
from pathlib import Path
import argparse
import pickle
from concurrent.futures import ThreadPoolExecutor, as_completed

def find_dot_files(directory, cfg_opt):
    """
    Recursively search the specified directory and return .dot files.
    """
    dot_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".dot"):
                if file.startswith("distance-"):
                    continue
                if cfg_opt:
                    if file.startswith("."):
                        print(f"[+]Add file {file}")
                        dot_files.append(os.path.join(root, file))
                else:
                    if not file.startswith("."):
                        print(f"[+]Add file {file}")
                        dot_files.append(os.path.join(root, file))
    return dot_files

def load_dot_file(dot_file):
    """
    Load a .dot file and return it as a networkx graph.
    """
    try:
        graph = nx.drawing.nx_pydot.read_dot(dot_file)
        if not isinstance(graph, (nx.Graph, nx.DiGraph, nx.MultiDiGraph)):
            raise ValueError("Loaded object is not a valid networkx graph.")
        return graph
    except Exception as e:
        print(f"Error loading {dot_file}: {e}")
        return None


def process_dot_files(dot_files):
    """
    Process the specified list of .dot files and merge them into a single graph.
    If the graph is a MultiDiGraph, use compose_all.
    """
    graph_list = []

    for dot_file in dot_files:
        graph = load_dot_file(dot_file)
        if graph is not None:
            print(f"Loaded .dot file: {dot_file}")
            graph_list.append(graph)

    # Check if any of the graphs are MultiDiGraph
    if any(isinstance(g, nx.MultiDiGraph) for g in graph_list):
        merged_graph = nx.compose_all(graph_list)  # Merge MultiDiGraph
    else:
        merged_graph = nx.DiGraph()  # Initialize an empty directed graph
        for g in graph_list:
            merged_graph = nx.compose(merged_graph, g)  # Merge DiGraphs

    return merged_graph  # Return the merged graph

def save_graph_to_pickle(graph, output_file):
    """
    Save the merged graph as a pickle file.
    """
    with open(output_file, 'wb') as f:
        pickle.dump(graph, f)
    print(f"Merged graph saved to {output_file}")

def main():
    # Process command-line arguments with argparse
    parser = argparse.ArgumentParser(description="Search and process .dot files in a directory")
    parser.add_argument('-d', '--directory', type=str, required=True, help="Directory to search for .dot files")
    parser.add_argument('--cfg', action='store_true', default=False, help="Parse Control Flow Graph")
    parser.add_argument('--max-workers', type=int, default=4, help="Max thread number")
    parser.add_argument('-o', '--output-directory', type=str, default=".", help="Directory to output graph file")

    args = parser.parse_args()

    directory = args.directory

    if not os.path.isdir(directory):
        print(f"Invalid directory: {directory}")
        return

    # Process .dot files
    dot_files = find_dot_files(directory, args.cfg)
    merged_graph = process_dot_files(dot_files)

    if args.cfg:
        filename = f"{args.output_directory}/cfg-graph.pickle"
    else:
        filename = f"{args.output_directory}/cg-graph.pickle"

    save_graph_to_pickle(merged_graph, filename)

if __name__ == "__main__":
    main()
