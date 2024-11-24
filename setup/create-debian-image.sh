#!/bin/bash

source $(dirname "$(realpath "${BASH_SOURCE[0]}")")/../config.sh

cd "${LKF_WORKDIR}"

"${SYZKALLER_DIR}/tools/create-image.sh" -a "${DEBIAN_ARCH}" -d "${DEBIAN_CODENAME}" 