# scripts/run_review.py
import json
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import time
from agents.bug_agent import find_issues_in_code
from agents.refactor_agent import refactor_code
from agents.explainer_agent import explain_changes

REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)

LANGUAGE_EXTENSIONS = {
    ".py": "Python",
    ".java": "Java",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".cpp": "C++",
    ".c": "C",
    ".cs": "C#",
    ".go": "Go",
    ".rb": "Ruby",
    ".sh": "Shell",
    ".rs": "Rust"
}

def run_pipeline_from_string(
    code: str,
    language: str = "Python"
):
    total_start = time.time()
    print(f"\n🚀 Starting [{language}] analysis...")

    # Step 1 — Analyze FIRST
    # Refactor needs this result
    print("1️⃣ Analyzing code...")
    t1 = time.time()
    issues = find_issues_in_code(
        code,
        language=language
    )
    print(f"   ✅ Analysis done in {time.time()-t1:.1f}s")

    # Step 2 — Refactor AND Explain TOGETHER
    # Both run at same time = saves 5 seconds!
    print("2️⃣ Refactoring + Explaining simultaneously...")
    t2 = time.time()

    refactored = None
    explanation = None

    with ThreadPoolExecutor(max_workers=2) as executor:

        # Submit BOTH at same time
        refactor_future = executor.submit(
            refactor_code,
            code,
            issues,
            language
        )

        explain_future = executor.submit(
            explain_changes,
            code,
            "",
            issues,
            language
        )

        # Get results
        refactored = refactor_future.result()
        explanation = explain_future.result()

    print(f"   ✅ Both done in {time.time()-t2:.1f}s")

    total = time.time() - total_start
    print(f"\n⚡ Total: {total:.1f} seconds")

    # Save reports
    ext = LANGUAGE_EXTENSIONS.get(
        f".{language.lower()}", ".py"
    )

    REPORT_DIR.joinpath("issues.json").write_text(
        json.dumps(issues, indent=2),
        encoding="utf-8"
    )
    REPORT_DIR.joinpath(
        f"refactored{ext}"
    ).write_text(refactored, encoding="utf-8")
    REPORT_DIR.joinpath(
        "explanation.txt"
    ).write_text(explanation, encoding="utf-8")

    return {
        "original_code": code,
        "issues": issues,
        "refactored_code": refactored,
        "explanation": explanation,
        "language": language,
        "processing_time": round(total, 1)
    }

def process_batch_files(uploaded_files):
    batch_results = {}

    for file in uploaded_files:
        try:
            ext = os.path.splitext(
                file.name
            )[1].lower()
            language = LANGUAGE_EXTENSIONS.get(
                ext, "Python"
            )
            file.seek(0)
            content = file.read().decode("utf-8")
            batch_results[file.name] = (
                run_pipeline_from_string(
                    content,
                    language=language
                )
            )
        except Exception as e:
            batch_results[file.name] = {
                "error": str(e)
            }

    return batch_results
