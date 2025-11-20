"""
Simple wrapper to run static analysis using agents/static_agent.py
"""

import argparse
from agents.static_agent import run_all

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--out", default="reports/static_report.json")
    args = parser.parse_args()
    run_all(args.repo, args.out)
    print("Static analysis complete:", args.out)
