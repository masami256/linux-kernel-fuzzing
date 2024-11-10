#!/bin/bash

source ../../config.sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")

parse_callgrah() {
    echo "[+]$(date) : Start parsing callgraph files"

    # Find call graph files.
    cgfiles=$(find "${LKF_LINUX_KERNEL_BUILD_ARTIFACT_DIR}" -name '*.bc.callgraph.dot' -a -not -name "distance-*")

    export SCRIPT_DIR

    echo "${cgfiles}" | xargs -n 1 -P 4 bash -c '
        f="$0"
        echo "[+]Parsing ${f}"
        "${SCRIPT_DIR}/calc-distance.py" "${f}"
    '

    echo "[+]$(date) : End parsing callgraph files"
}

parse_control_flow_graph() {
    echo "[+]$(date) : Start parsing control flow graph files"

    # Find call graph files.
    cfgfiles=$(find "${LKF_CFG_FILES_OUTPUT_DIR}" -name '*.dot' -a -not -name "distance-*")

    export SCRIPT_DIR

    echo "${cfgfiles}" | xargs -n 1 -P 4 bash -c '
        f="$0"
        echo "[+]Parsing ${f}"
        "${SCRIPT_DIR}/calc-distance.py" "${f}"
    '

    echo "[+]$(date) : End parsing callparsing control flow graphgraph files"
}

parse_callgrah
parse_control_flow_graph

echo "[+]Done."
