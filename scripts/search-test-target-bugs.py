#!/usr/bin/env python3

import sys
import os
import argparse
import glob
import subprocess
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import semantic_version
import yaml
import pprint

CHECK_CIP_KERNEL = "cip"
CHECK_CIP_RT_KERNEL = "cip-rt"
CHECK_CIP_ST_KERNEL = "cip-st"
CHECK_STABLE_KERNEL = "stable"
CHECK_STABLE_RT_KERNEL = "stable-rt"
CHECK_MAINLINE_KERNEL = "mainline"

KERNEL_MAP = {
    CHECK_CIP_KERNEL: CHECK_CIP_KERNEL,
    CHECK_CIP_RT_KERNEL: CHECK_CIP_RT_KERNEL,
    CHECK_CIP_ST_KERNEL: CHECK_CIP_ST_KERNEL,
    CHECK_STABLE_KERNEL: CHECK_STABLE_KERNEL,
    CHECK_STABLE_RT_KERNEL: CHECK_STABLE_RT_KERNEL,
    CHECK_MAINLINE_KERNEL: CHECK_MAINLINE_KERNEL,
}

def get_target_kernel_name(target_kernel, kernel_version):
    logging.debug(f"target_kernel: {target_kernel}, kernel_version: {kernel_version}")

    if target_kernel == CHECK_CIP_KERNEL:
        return f"cip/{kernel_version}"
    elif target_kernel == CHECK_CIP_RT_KERNEL:
        return f"cip/{kernel_version}-rt"
    elif target_kernel == CHECK_CIP_ST_KERNEL:
        return f"cip/{kernel_version}-st"
    elif target_kernel == CHECK_STABLE_KERNEL:
        return f"stable/{kernel_version}"
    elif target_kernel == CHECK_STABLE_RT_KERNEL:
        return f"stable/{kernel_version}-rt"
    elif target_kernel == CHECK_MAINLINE_KERNEL:
        return "mainline"

    sys.exit("Error: Invalid target kernel")

def find_first_version(git_repo, commit_hash, target_kernel, kernel_name, suffix):
    print(f"Searching for first version containing {commit_hash} in {target_kernel}")
    cmd = ['git', 'tag', '--sort=taggerdate', '--contains', commit_hash, '-l', 'v*']
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=git_repo)
    if res.returncode:
        print(f"Couldn't find any tag containing {commit_hash}: msg: {res.stderr}")
        return None

    all_tags = [tag for tag in res.stdout.split('\n') if tag]
    tags_tmp = []

    print(f"checking {target_kernel}")
    if target_kernel in {CHECK_MAINLINE_KERNEL, CHECK_STABLE_KERNEL}:
        # remove -st, -rt, -cip tags
        tags_tmp.extend([tag for tag in all_tags if "-cip" not in tag and "-st" not in tag and "-rt" not in tag])
    elif target_kernel == CHECK_CIP_KERNEL:
        # search -cipXX tag which should not contain -rt
        tags_tmp.extend([tag for tag in all_tags if "-st" not in tag and "-rt" not in tag])
    elif target_kernel == CHECK_CIP_RT_KERNEL:
        # search -cipXX-rtYY
        tags_tmp.extend([tag for tag in all_tags if "-st" not in tag])
    elif target_kernel == CHECK_CIP_ST_KERNEL:
        # search -st tag
        tags_tmp.extend([tag for tag in all_tags if not "-cip" in tag and not "-rt" in tag])
    elif target_kernel == CHECK_STABLE_RT_KERNEL:
        # search -rtYY tag which should not contain -cip and -st
        tags_tmp.extend([tag for tag in all_tags if not "-cip" in tag and "-st" not in tag])
    else:
        print(f"Unknown target_kernel: {target_kernel}")
    
    tags = []
    for tag in tags_tmp:
        tags.append(semantic_version.Version.coerce(tag[1:]))  # Remove 'v' prefix and convert

    if not tags:
        print(f"Couldn't find any tag containing {commit_hash}")
        return None
    
    sorted(tags, reverse=False)
    if target_kernel in {CHECK_MAINLINE_KERNEL, CHECK_STABLE_KERNEL}:
        return str(tags[0])
    elif target_kernel == CHECK_CIP_KERNEL:
        idx = next((i for i, s in enumerate(tags) if "-cip" in s), -1)
        if not tag == -1:
            return str(tags[idx])

def read_cip_kernel_sec_files(cip_kernel_sec_dir, kernel_dir, cve_year, kernel_version, target_kernel):
    cves = {}
    target = get_target_kernel_name(target_kernel, kernel_version)

    search_path = os.path.join(cip_kernel_sec_dir, "issues")
    print(f"Searching CVEs for {target}")

    for file in glob.glob(os.path.join(search_path, "*.yml")):
        cve = os.path.splitext(os.path.basename(file))[0]
        if cve_year and not cve.startswith(f"CVE-{cve_year}-"):
            continue
        
        if not cve == "CVE-2025-21681":
            continue

        with open(file, "r") as f:
            data = yaml.safe_load(f)

        if data["description"].startswith("[REJECTED]"):
            continue

        cves[cve] = {
            "description": data["description"].strip()[:80],
            "introduced-by": {},
            "introduced-version": {},
            "fixed-by": {},
            "fixed-version": {},
        }

        for key in ["introduced-by", "fixed-by"]:
            if key in data:
                for k in [target, "mainline"]:
                    if k in data[key]:
                        tmp = k.split("/")[0]
                        kernel_name = tmp[0]
                        kernel_suffix = None
                        if len(tmp) > 1:
                            if tmp[1] in"rt":
                                suffix = "-rt"
                            elif tmp[1] in "st":
                                suffix = "-st"
                            
                        print(f"tmp: {tmp}")
                        cves[cve][key][k] = data[key][k]
                        if key == "introduced-by":
                            cves[cve]["introduced-version"][k] = find_first_version(kernel_dir, data[key][k][0], kernel_name, suffix)
                        elif key == "fixed-by":
                            cves[cve]["fixed-version"][k] = find_first_version(kernel_dir, data[key][k][0], kernel_name, suffix)

    print(f"Found {len(cves)} CVEs")
    return cves

def parse_args():
    parser = argparse.ArgumentParser(description="Search for test target bugs")
    parser.add_argument("--kernel-dir", required=True, help="Linux kernel directory", metavar="path")
    parser.add_argument("--kernel-version", required=True, help="Linux kernel version", metavar="version")
    parser.add_argument("--kernel-branch", default="master", help="Linux kernel branch", metavar="branch")
    parser.add_argument("--remote-name", default="origin", help="Remote name", metavar="name")
    parser.add_argument("--cip-kernel-sec", required=True, help="Path to the cip-kernel-sec directory", metavar="path")
    parser.add_argument("--target_kernel", help=f"target_kernel\n{KERNEL_MAP}", metavar="target_kernel")
    parser.add_argument("--cve-year", default=None, help="CVE year", metavar="year")
    parser.add_argument("--output", default="cve-list.yml", help="Output file", metavar="file")
    parser.add_argument("--threads", type=int, default=4, help="Number of threads for parallel processing", metavar="num_threads")
    return parser.parse_args()

def main():
    args = parse_args()

    target_kernel = args.target_kernel

    cves = read_cip_kernel_sec_files(args.cip_kernel_sec, args.kernel_dir, args.cve_year, args.kernel_version, target_kernel)

    with open(args.output, "w") as f:
        yaml.dump(cves, f)
    print(f"CVE data was written to {args.output}")

if __name__ == "__main__":
    main()
