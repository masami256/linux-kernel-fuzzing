#!/usr/bin/env python3

import semantic_version
import pprint

v1 = semantic_version.Version("platform-drivers-x86-v3.17-1")
v2 = semantic_version.Version("4.18.0-st2")

print(f"v1 > v2: {v1 > v2}")