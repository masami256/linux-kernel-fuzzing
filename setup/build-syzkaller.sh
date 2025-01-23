#!/bin/bash

source $(dirname "$(realpath "${BASH_SOURCE[0]}")")/../config.sh

cd "${LKF_WORKDIR}"

git clone https://github.com/google/syzkaller.git
cd syzkaller

git checkout 9d4f14f879d34d715f61d84f4b1144e9fa8ca236

make

GOOS=linux GOARCH=amd64 go build -ldflags="-s -w" -o ./bin/syz-cover github.com/google/syzkaller/tools/syz-cover