#!/bin/bash

source $(dirname "$(realpath "${BASH_SOURCE[0]}")")/../config.sh

export LLVM_BUILD="${LKF_LLVM_INSTALL_DIR}"

cd "${DEEPTYPE_DIR}"

make
