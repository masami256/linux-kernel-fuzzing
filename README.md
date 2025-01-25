# linux-kernel-fuzzing

# Build LLVM and DeepType

Go to setupl directory.

```
cd setup
```

Run build-llvm.sh to build llvm

```
./build-llvm.sh
```

Run build-deeptye.sh to build DeepType.

```
./build-deeptype.sh
```

# Build IRDumper

Go to IRDumper directory.

```
cd IRDumper
```

Then run make command.

```
make
```

# Build IRAnalyzer

```
cd scripts
```

Then run build-iranalyzer.sh.

```
./build-iranalyzer.sh
```

# Build linux kernel

Go to kernel directoy

```
cd scripts
```

The run build-kernel.sh.

```
./build-kernel.sh <path to linux kernel source directory>
```

# Create bc file list
```
./scripts/create-bclist.sh <path to linux kernel source directory>
```

# Analyze call graph

```
./DeepType/build/lib/kanalyzer @bc.list
```

# Create unified call graph

```
./scripts/create-callgraph.py <path to bcfiles directory> <output directory>
```

# Find path

```
./scripts/find-path.py ./unified_call_graph.pkl <function name>
```

# Find memory related operations

```
./scripts/find-memory-related-ops.py [memory operation option] <path to call graph json files directory>
```

# Create bb-info json

```
./IRAnalyzer/build/iranalyzer @bc.list
```

# Analyze memory ops functions

```
./scripts/merge-data.py --bcfiles-dir <path to bcfiles directory> --memory-ops-json <path to memory ops json> --bb-info-json <path to bb-info.json>
```

# Using docker

```
docker compose build
docker compose run --service-ports linux-kernel-fuzzing
```