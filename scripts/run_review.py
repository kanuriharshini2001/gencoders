import json
from pathlib import Path
from agents.static_agent import analyze_code
from agents.refactor_agent import refactor_code
from agents.bug_agent import find_issues_in_code
from agents.explainer_agent import explain_changes
from agents.refactor_agent import refactor_code

REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)

def run_pipeline_from_string(code: str):
    issues = analyze_code(code)
    refactored = refactor_code(code, issues)
    explanation = explain_changes(code, refactored, issues)

    REPORT_DIR.joinpath("issues.json").write_text(json.dumps(issues, indent=2))
    REPORT_DIR.joinpath("refactored.py").write_text(refactored)
    REPORT_DIR.joinpath("explanation.txt").write_text(explanation)

    return {
        "issues": issues,
        "refactored_code": refactored,
        "explanation": explanation
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 2:
        path = Path(sys.argv[1])
        code = path.read_text()
        run_pipeline_from_string(code)
        print("Done. Reports saved.")
    else:
        print("Usage: python -m scripts.run_review <file.py>")
