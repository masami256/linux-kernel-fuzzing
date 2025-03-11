#!/bin/bash

source $(dirname "$(realpath "${BASH_SOURCE[0]}")")/../config.sh

cd "${LKF_WORKDIR}"

git clone https://github.com/google/syzkaller.git
cd syzkaller

git checkout 9be4ace34ffed29b36f379311c49249a457dabf3

make

GOOS=linux GOARCH=amd64 go build -ldflags="-s -w" -o ./bin/syz-cover github.com/google/syzkaller/tools/syz-cover
GOOS=linux GOARCH=amd64 go build -ldflags="-s -w" -o ./bin/syz-reporter github.com/google/syzkaller/tools/syz-reporter
GOOS=linux GOARCH=amd64 go build -ldflags="-s -w" -o ./bin/syz-repro github.com/google/syzkaller/tools/syz-repro
GOOS=linux GOARCH=amd64 go build -ldflags="-s -w" -o ./bin/syz-crush github.com/google/syzkaller/tools/syz-crush