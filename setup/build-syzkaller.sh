#!/bin/bash

source $(dirname "$(realpath "${BASH_SOURCE[0]}")")/../config.sh

cd "${LKF_WORKDIR}"

git clone https://github.com/google/syzkaller.git
cd syzkaller

git checkout f5427d7cf8bff4a8e0647b95351bea3d20e0654e

make

GOOS=linux GOARCH=amd64 go build -ldflags="-s -w" -o ./bin/syz-cover github.com/google/syzkaller/tools/syz-cover