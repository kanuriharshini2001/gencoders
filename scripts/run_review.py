import json
import sys
from pathlib import Path

# Import your agents
from agents.bug_agent import find_issues_in_code
from agents.refactor_agent import refactor_code
from agents.explainer_agent import explain_changes

REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)

# --- THIS IS THE FUNCTION YOUR APP IS LOOKING FOR ---
def run_pipeline_from_string(code: str):
    """
    Runs the full review pipeline on a raw string of Python code.
    Used by both the CLI and the Streamlit UI.
    """
    print("--- Starting Analysis ---")

    # 1. Use the Fixed Bug Agent
    print("1. Analyzing code...")
    issues = find_issues_in_code(code)
    
    # 2. Refactor
    print("2. Refactoring code...")
    refactored = refactor_code(code, issues)
    
    # 3. Explain
    print("3. Generating explanation...")
    explanation = explain_changes(code, refactored, issues)

    # 4. Save Reports
    REPORT_DIR.joinpath("issues.json").write_text(json.dumps(issues, indent=2), encoding="utf-8")
    REPORT_DIR.joinpath("refactored.py").write_text(refactored, encoding="utf-8")
    REPORT_DIR.joinpath("explanation.txt").write_text(explanation, encoding="utf-8")

    # 5. Return for Streamlit
    return {
        "original_code": code,  # 
        "issues": issues,
        "refactored_code": refactored,
        "explanation": explanation
    }
# --- BATCH PROCESSING FUNCTION (Optional but good for v1.1) ---
def process_batch_files(uploaded_files):
    batch_results = {}
    for file in uploaded_files:
        try:
            file.seek(0)
            content = file.read().decode("utf-8")
            batch_results[file.name] = run_pipeline_from_string(content)
        except Exception as e:
            batch_results[file.name] = {"error": str(e)}
    return batch_results

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        path = Path(sys.argv[1])
        if path.exists():
            code_content = path.read_text(encoding="utf-8")
            run_pipeline_from_string(code_content)
            print(f"\nDone! Reports saved to {REPORT_DIR}")
        else:
            print(f"Error: File {path} not found.")
    else:
        print("Usage: python -m scripts.run_review <file.py>")