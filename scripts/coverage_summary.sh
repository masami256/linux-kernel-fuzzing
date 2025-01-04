#!/bin/bash

if [ $# -ne 2 ]; then
    echo "[*]usage: $0 <syzkaller config> <raw coverage file>"
    exit 1
fi

source $(dirname "$(realpath "${BASH_SOURCE[0]}")")/../config.sh
cfg=$(realpath "$1")
rawcoverage=$(realpath "$2")

coverage_dir="${LKF_WORKDIR}/covarages"
rm -fr "${coverage_dir}" || true
mkdir "${coverage_dir}"

cd "${LKF_WORKDIR}"/..
${LKF_WORKDIR}/syzkaller/bin/syz-cover -config "${cfg}" -exports all "${rawcoverage}"

exit 0