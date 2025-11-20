"""
CLI helper to refactor a single file and produce a .diff patch in reports/patches.
"""

import argparse
from agents.refactor_agent import refactor_file, save_patch

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    parser.add_argument("--out", default="reports/patches")
    parser.add_argument("--mock", action="store_true")
    args = parser.parse_args()
    res = refactor_file(args.file, mock=args.mock or True)
    p = save_patch(res, out_dir=args.out)
    print("Patch saved to:", p)
