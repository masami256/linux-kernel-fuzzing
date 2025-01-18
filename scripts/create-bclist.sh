#!/bin/bash

if [ $# != 1 ]; then
    echo "usage: $0 [path to bcfiles directory]"
    exit 1
fi

srcdir=$1
bcfiles_tmp=$(find "${srcdir}" -name "*.bc")

bcfiles=()

for tmp in $bcfiles_tmp;
do
    ret=$(file "${tmp}" | grep "LLVM IR bitcode" >/dev/null ; echo $?)
    if [ "$ret" = "0" ]; then
        bcfiles+=("$tmp")
    fi
done

bclist="bc.list"
if [ -f "${bclist}" ]; then
    rm -f "${bclist}"
fi

for tmp in "${bcfiles[@]}";
do
    echo "${tmp}" >> "${bclist}"
done

echo "Done."
