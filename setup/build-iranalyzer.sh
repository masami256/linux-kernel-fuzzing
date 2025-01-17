#!/bin/bash

source $(dirname "$(realpath "${BASH_SOURCE[0]}")")/../config.sh

export LLVM_BUILD="${LKF_LLVM_INSTALL_DIR}"

D=$(dirname "$(realpath "${BASH_SOURCE[0]}")")/../IRAnalyzer
cd "${D}"

make
