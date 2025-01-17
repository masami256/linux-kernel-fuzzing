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