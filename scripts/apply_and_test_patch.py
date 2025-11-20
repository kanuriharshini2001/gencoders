"""
Apply patch to sandbox copy and run pytest.
This is a safe dry-run: it copies repo to sandbox, applies refactored file content and runs pytest.
"""

import shutil
from pathlib import Path
import subprocess
import argparse
import json

def apply_patch_direct(sandbox_dir, target_file, refactored_code):
    target_path = Path(sandbox_dir) / target_file
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(refactored_code)

def run_pytest(sandbox_dir):
    try:
        out = subprocess.check_output(["pytest", "-q"], cwd=sandbox_dir, universal_newlines=True, stderr=subprocess.STDOUT, timeout=120)
        return True, out
    except subprocess.CalledProcessError as e:
        return False, e.output
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--patch-meta", required=True, help="JSON file with refactored code and original path (produced by refactor agent)")
    parser.add_argument("--sandbox", default="data/sandbox_repo")
    args = parser.parse_args()

    repo = args.repo
    sandbox = args.sandbox
    # copy repo
    shutil.rmtree(sandbox, ignore_errors=True)
    shutil.copytree(repo, sandbox)
    meta = json.load(open(args.patch_meta, "r", encoding="utf-8"))
    # meta expected to contain refactored_code and original_path
    refactored_code = meta.get("refactored_code")
    original_path = meta.get("original_path")
    # original_path is absolute or relative path; make it relative to repo root
    rel = Path(original_path).name  # simplifying: use filename only
    apply_patch_direct(sandbox, rel, refactored_code)
    ok, out = run_pytest(sandbox)
    print("Pytest result:", ok)
    print(out)
