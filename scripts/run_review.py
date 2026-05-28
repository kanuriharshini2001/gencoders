import json
import sys
from pathlib import Path

# Import your agents
from agents.bug_agent import find_issues_in_code
from agents.refactor_agent import refactor_code
from agents.explainer_agent import explain_changes

REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)

# Language to file extension mapping for saving reports
LANGUAGE_EXTENSIONS = {
    "Python": ".py",
    "Java": ".java",
    "JavaScript": ".js",
    "TypeScript": ".ts",
    "C++": ".cpp",
    "C": ".c",
    "C#": ".cs",
    "Go": ".go",
    "Ruby": ".rb",
    "Shell": ".sh",
    "Rust": ".rs",
    "PHP": ".php",
    "Kotlin": ".kt",
    "Swift": ".swift"
}

def run_pipeline_from_string(code: str, language: str = "Python"):
    """
    Runs the full review pipeline on a raw string of code.
    Supports multiple programming languages.
    Used by both the CLI and the Streamlit UI.
    """
    print(f"--- Starting Analysis [{language}] ---")

    # 1. Analyze bugs — pass language to agent
    print(f"1. Analyzing {language} code...")
    issues = find_issues_in_code(code, language=language)

    # 2. Refactor — pass language to agent
    print(f"2. Refactoring {language} code...")
    refactored = refactor_code(code, issues, language=language)

    # 3. Explain
    print("3. Generating explanation...")
    explanation = explain_changes(code, refactored, issues)

    # 4. Save Reports
    ext = LANGUAGE_EXTENSIONS.get(language, ".py")
    REPORT_DIR.joinpath("issues.json").write_text(
        json.dumps(issues, indent=2), encoding="utf-8"
    )
    REPORT_DIR.joinpath(f"refactored{ext}").write_text(
        refactored, encoding="utf-8"
    )
    REPORT_DIR.joinpath("explanation.txt").write_text(
        explanation, encoding="utf-8"
    )

    # 5. Return for Streamlit
    return {
        "original_code": code,
        "issues": issues,
        "refactored_code": refactored,
        "explanation": explanation,
        "language": language  # ✅ Pass language back to UI
    }

# --- BATCH PROCESSING ---
def process_batch_files(uploaded_files):
    """
    Process multiple files detecting language automatically.
    """
    import os
    
    # Language detection from extension
    extensions = {
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
        ".rs": "Rust",
        ".php": "PHP",
        ".kt": "Kotlin",
        ".swift": "Swift"
    }

    batch_results = {}
    for file in uploaded_files:
        try:
            # Detect language from filename
            ext = os.path.splitext(file.name)[1].lower()
            language = extensions.get(ext, "Python")
            
            file.seek(0)
            content = file.read().decode("utf-8")
            
            # Run pipeline with detected language
            batch_results[file.name] = run_pipeline_from_string(
                content,
                language=language
            )
        except Exception as e:
            batch_results[file.name] = {"error": str(e)}
    
    return batch_results

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        path = Path(sys.argv[1])
        if path.exists():
            # Detect language from file extension
            extensions = {
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
                ".rs": "Rust",
                ".php": "PHP",
                ".kt": "Kotlin",
                ".swift": "Swift"
            }
            ext = path.suffix.lower()
            language = extensions.get(ext, "Python")
            
            print(f"Detected language: {language}")
            code_content = path.read_text(encoding="utf-8")
            run_pipeline_from_string(code_content, language=language)
            print(f"\nDone! Reports saved to {REPORT_DIR}")
        else:
            print(f"Error: File {path} not found.")
    else:
        print("Usage: python -m scripts.run_review <file>")
        print("Supported: .py .java .js .ts .cpp .c .cs .go .rb .sh .rs .php .kt .swift")
