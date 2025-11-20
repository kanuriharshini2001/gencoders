"""
Ingest a repo: clone via Git or copy local path to data directory.
"""

import argparse
import os
from git import Repo
from pathlib import Path
import shutil


def clone_repo(url, out_dir):
    # If directory exists, remove it safely
    if os.path.exists(out_dir):
        print("Removing existing out_dir:", out_dir)
        shutil.rmtree(out_dir, ignore_errors=True)

    print(f"Cloning {url} into {out_dir} ...")
    Repo.clone_from(url, out_dir)
    return out_dir


def copy_local(path, out_dir):
    # If folder exists, delete it safely
    if os.path.exists(out_dir):
        print(f"Removing existing folder: {out_dir}")
        shutil.rmtree(out_dir, ignore_errors=True)

    print(f"Copying local folder {path} → {out_dir}")
    shutil.copytree(
        path,
        out_dir,
        ignore=shutil.ignore_patterns('.git'),
        dirs_exist_ok=True   # <-- FIX
    )
    return out_dir



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, help="git url or local path")
    parser.add_argument("--out", default="data/repo")
    args = parser.parse_args()

    # Detect Git URL
    if args.repo.startswith("http://") or args.repo.startswith("https://") or args.repo.endswith(".git"):
        clone_repo(args.repo, args.out)
    else:
        copy_local(args.repo, args.out)

    print("Repo ingested to", args.out)
