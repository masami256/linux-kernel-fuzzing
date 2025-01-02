#!/bin/bash

source $(dirname "$(realpath "${BASH_SOURCE[0]}")")/../config.sh

cd "${LKF_WORKDIR}"

git clone https://github.com/google/syzkaller.git
cd syzkaller

git checkout 68da6d951a345757b69b764ceb8dda1e9d65b038

make

GOOS=linux GOARCH=amd64 go build -ldflags="-s -w" -o ./bin/syz-cover github.com/google/syzkaller/tools/syz-cover