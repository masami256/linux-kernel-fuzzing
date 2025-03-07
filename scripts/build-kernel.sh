#!/bin/bash

if [ $# -lt 1 ]; then
    echo "[*]usage $0 <linux kernel directory> <config file path>"
    exit 1
fi

source $(dirname "$(realpath "${BASH_SOURCE[0]}")")/../config.sh

KERNEL_DIR=$(realpath $1)
CONFIG_FILE=""
if [ "$2" != "" ]; then
    CONFIG_FILE=$(realpath "$2")
fi

export PATH="${LKF_LLVM_INSTALL_DIR}/bin:${PATH}"

echo "clang is ${LKF_CLANG}"
cd "${KERNEL_DIR}"

rm -fr "${KERNEL_DIR}/bcfiles" || true

make LLVM=1 CC="${LKF_CLANG}" clean
make LLVM=1 CC="${LKF_CLANG}" mrproper

git ls-files --others --exclude-standard | xargs rm -f
git checkout Makefile
cp Makefile Makefile.bak

MY_KBUILD_USERCFLAGS="-Wno-error -g -Xclang -no-opaque-pointers -Xclang -disable-O0-optnone -fpass-plugin=${IRDUMPER}"
MY_KBUILD_CFLAGS="-Wno-error -g -Xclang -no-opaque-pointers -Xclang -disable-O0-optnone -fpass-plugin=$IRDUMPER"

echo "KBUILD_USERCFLAGS += ${MY_KBUILD_USERCFLAGS}" >> Makefile
echo "KBUILD_CFLAGS += ${MY_KBUILD_CFLAGS}" >> Makefile

if [ "${CONFIG_FILE}" = "" ]; then
    make LLVM=1 CC="${LKF_CLANG}" defconfig
    make LLVM=1 CC="${LKF_CLANG}" kvm_guest.config

    ./scripts/config -e KCOV
    ./scripts/config -e KCOV_INSTRUMENT_ALL
    ./scripts/config -e KCOV_ENABLE_COMPARISONS
    ./scripts/config -e DEBUG_FS
    ./scripts/config -e DEBUG_KMEMLEAK
    ./scripts/config -e DEBUG_INFO_DWARF_TOOLCHAIN_DEFAULT
    ./scripts/config -e KALLSYM
    ./scripts/config -e KALLSYMS_ALL
    ./scripts/config -e NAMESPACES
    ./scripts/config -e UTS_NS
    ./scripts/config -e IPC_NS
    ./scripts/config -e PID_NS
    ./scripts/config -e NET_NS
    ./scripts/config -e CGROUP_PIDS
    ./scripts/config -e MEMCG
    ./scripts/config -e USER_NS
    ./scripts/config -e KASAN
    ./scripts/config -e KASAN_INLINE
    ./scripts/config -e KFENCE
    ./scripts/config -e CONFIGFS_FS
    ./scripts/config -e SECURITYFS
    ./scripts/config -e CMDLINE_BOOL
    ./scripts/config --set-val CMDLINE "net.ifnames=0"
    ./scripts/config -d RANDOMIZE_BASE
    ./scripts/config -e HARDENED_USERCOPY
    ./scripts/config -e FORTIFY_SOURCE

    make LLVM=1 CC="${LKF_CLANG}" olddefconfig
else
    echo "[+]Use ${CONFIG_FILE} as a .config"
    cp -f "${CONFIG_FILE}" "${KERNEL_DIR}/.config"
    make LLVM=1 CC="${LKF_CLANG}" olddefconfig
fi

echo "[+]$(date) : Start build"
make LLVM=1 CC="${LKF_CLANG}" V=1 -j$(nproc)
echo "[+]$(date) : End build"
echo "[+]*.bc files are stored in ${KERNEL_DIR}/bcfiles"

