CUR_DIR = $(shell pwd)
LLVM_BUILD := $(LLVM_BUILD)
IRANALYZER_DIR := ${CUR_DIR}/src
IRANALYZER_BUILD := ${CUR_DIR}/build

NPROC := ${shell sysctl -n hw.ncpu}

build_src_func = \
	(mkdir -p ${2} \
		&& cd ${2} \
		&& PATH=${LLVM_BUILD}/bin:${PATH}\
			LLVM_ROOT_DIR=${LLVM_BUILD}/bin \
			LLVM_LIBRARY_DIRS=${LLVM_BUILD}/lib \
			LLVM_INCLUDE_DIRS=${LLVM_BUILD}/include \
			CC=clang CXX=clang++ \
			cmake ${1} \
				-DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_CXX_FLAGS_RELEASE="-std=c++14 -fno-rtti -fpic -O3 -v" \
		&& make -j${NPROC})

all: iranalyzer

iranalyzer:
	$(call build_src_func, ${IRANALYZER_DIR}, ${IRANALYZER_BUILD})

clean:
	rm -rf ${IRANALYZER_BUILD}
