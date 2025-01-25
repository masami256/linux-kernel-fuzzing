#!/bin/bash

source $(dirname "$(realpath "${BASH_SOURCE[0]}")")/../config.sh

cd "${LKF_WORKDIR}"

mkdir -p "${DEBIAN_IMAGE_DIR}"
cd "${DEBIAN_IMAGE_DIR}"
"${SYZKALLER_DIR}/tools/create-image.sh" -a "${DEBIAN_ARCH}" -d "${DEBIAN_CODENAME}" 