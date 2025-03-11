#!/bin/bash

if [ $# -lt 1 ]; then
    echo "[*]usage $0 <linux kernel directory>"
    exit 1
fi

KERNEL_DIR=$(realpath $1)

source $(dirname "$(realpath "${BASH_SOURCE[0]}")")/../config.sh

CERTS_DIR="${LKF_WORKDIR}/certs"

if [ ! -d "${CERTS_DIR}" ]; then
    mkdir -p "${CERTS_DIR}"
fi

cd "${CERTS_DIR}"

openssl req -new -nodes -utf8 -sha256 -days 36500 -batch -x509 \
   -config x509.genkey -outform PEM -out fuzzing_kernel_signing_cert.pem \
   -keyout fuzzing_kernel_signing_cert.pem

cp fuzzing_kernel_signing_cert.pem "${KERNEL_DIR}/certs/signing_key.pem"

echo "Done."

