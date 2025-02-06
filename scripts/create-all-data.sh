#!/bin/bash
set -e

source $(dirname "$(realpath "${BASH_SOURCE[0]}")")/../config.sh

if [ -z "$1" ]; then
    echo "Usage: $0 <path-to-linux-kernel>"
    exit 1
fi
bcfiles_dir=$(realpath "$1")/bcfiles/

if [ ! -f "bc.list" ]; then
    echo "bc.list is not found. Please create it first."
    exit 1
fi

rm -f file_analysis_* || true
rm -f merged.json || true
rm -f function_analysis_output.json || true
rm -f bb_info.json || true
rm -f cg_data.json || true

"${LKF_BASE_PATH}/scripts/find-memory-related-ops.py" --kmalloc --dir "${bcfiles_dir}" 

"${LKF_BASE_PATH}/IRAnalyzer/build/iranalyzer" @bc.list

"${LKF_BASE_PATH}/scripts/merge-data.py" \
  --bcfiles-dir "${bcfiles_dir}" \
  --bb-info-json "${LKF_BASE_PATH}/bb_info.json"