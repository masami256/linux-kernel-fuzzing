#!/bin/bash

if [ $# -lt 1 ]; then
    echo "[*]usage $0 <linux kernel directory> <config file path>"
    exit 1
fi

source ../config.sh

KERNEL_DIR="$1"
CONFIG_FILE="$2"

echo "clang is ${LKF_CLANG}"
cd "${KERNEL_DIR}"

make LLVM=1 CC="${LKF_CLANG}" clean
make LLVM=1 CC="${LKF_CLANG}" mrproper

git ls-files --others --exclude-standard | xargs rm -f
git checkout Makefile
cp Makefile Makefile.bak

MY_KBUILD_USERCFLAGS="-Wno-error -g -Xclang -no-opaque-pointers -fpass-plugin=${IRDUMPER}"
MY_KBUILD_CFLAGS="-Wno-error -g -Xclang -no-opaque-pointers -fpass-plugin=$IRDUMPER"

echo "KBUILD_USERCFLAGS += ${MY_KBUILD_USERCFLAGS}" >> Makefile
echo "KBUILD_CFLAGS += ${MY_KBUILD_CFLAGS}" >> Makefile

if [ "${CONFIG_FILE}" = "" ]; then
    make LLVM=1 CC="${LKF_CLANG}" defconfig
else
    cp "${CONFIG_FILE}" ./.config
    make LLVM=1 CC="${LKF_CLANG}" olddefconfig
fi

make LLVM=1 CC="${LKF_CLANG}" kvm_guest.config

./scripts/config -e KCOV
./scripts/config -e DEBUG_INFO_DWARF4 
./scripts/config -e KASAN
./scripts/config -e KASAN_INLINE
./scripts/config -e KFENCE
./scripts/config -e CONFIGFS_FS
./scripts/config -e SECURITYFS
./scripts/config -e CMDLINE_BOOL
./scripts/config --set-val CMDLINE "net.ifnames=0"

make LLVM=1 CC="${LKF_CLANG}" olddefconfig

echo "[+]$(date) : Start build"
make LLVM=1 CC="${LKF_CLANG}" -j$(nproc)
echo "[+]$(date) : End build"


