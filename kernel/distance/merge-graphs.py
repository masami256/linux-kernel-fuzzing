#!/usr/bin/env python3

import os
import networkx as nx
from pathlib import Path
import argparse
import pickle

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
    return nx.drawing.nx_pydot.read_dot(dot_file)

def process_dot_files(dot_files):
    """
    Process the specified list of .dot files sequentially.
    """
    graphs = []

    for dot_file in dot_files:
        try:
            graph = load_dot_file(dot_file)
            if graph is not None:
                print(f"Loaded .dot file: {dot_file}")
                graphs.append(graph)
        except Exception as e:
            print(f"Error loading {dot_file}: {e}")

    return graphs


def save_graphs_to_pickle(graphs, output_file):
    """
    Save the list of graphs as a single pickle file.
    """
    with open(output_file, 'wb') as f:
        pickle.dump(graphs, f)
    print(f"All graphs saved to {output_file}")

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
    graphs = process_dot_files(dot_files)

    if args.cfg:
        filename = f"{args.output_directory}/cfg-graphs.pickle"
    else:
        filename = f"{args.output_directory}/cg-graphs.pickle"

    save_graphs_to_pickle(graphs, filename)

if __name__ == "__main__":
    main()
