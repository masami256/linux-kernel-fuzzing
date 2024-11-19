#!/bin/bash

source $(dirname "$(realpath "${BASH_SOURCE[0]}")")/../config.sh

set -e

download_and_unpack_llvm() {
    local llvm_src_tar_gz="llvmorg-${LKF_LLVM_VERSION}.tar.gz"
    wget -P "${LKF_LLVM_BUILD_DIR}" "https://github.com/llvm/llvm-project/archive/refs/tags/${llvm_src_tar_gz}"
    tar xf "${LKF_LLVM_BUILD_DIR}/${llvm_src_tar_gz}" -C "${LKF_LLVM_BUILD_DIR}/"
}

build_llvm() {
    cmake -S llvm -B build -G Ninja -DCMAKE_INSTALL_PREFIX="${LKF_LLVM_INSTALL_DIR}" \
        -DCMAKE_BUILD_TYPE=Release -DLLVM_ENABLE_PROJECTS="clang;lld"

    cmake --build build
    ninja -C "${LKF_LLVM_SRC_UNPACK_DIR}/build" install
}

echo "[+]LLVM build directory is ${LKF_LLVM_BUILD_DIR}"

if [[ -d "${LKF_LLVM_BUILD_DIR}" ]]; then
    echo "[+]Remove old ${LKF_LLVM_BUILD_DIR} directory"
    rm -fr "${LKF_LLVM_BUILD_DIR}"
fi

mkdir -p "${LKF_LLVM_BUILD_DIR}"

download_and_unpack_llvm

pushd .
cd "${LKF_LLVM_SRC_UNPACK_DIR}"

build_llvm

popd
echo "[+] Done"
