#!/bin/bash

if [ "$#" != "1" ]; then
    echo "[*] usage: $0 <config file>"
    exit 1
fi

cfgfile=$(realpath "$1")

fuzzing_execution_time="490m"
sleep_time="480m"

source $(dirname "$(realpath "${BASH_SOURCE[0]}")")/../config.sh

echo "${LKF_WORKDIR}/syzkaller/bin/syz-manager" -config "${cfgfile}" 

timeout "${fuzzing_execution_time}" "${LKF_WORKDIR}/syzkaller/bin/syz-manager" -config "${cfgfile}" &
sleep "${sleep_time}"
wget http://localhost:56741/rawcover

echo "Done"
exit 0