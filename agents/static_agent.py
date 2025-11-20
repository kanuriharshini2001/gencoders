"""
Static Analysis Agent
Performs basic static checks like unused variables, long lines, missing docstrings, etc.
"""

def analyze_code(code: str):
    issues = []

    # Example check: long lines
    for i, line in enumerate(code.split("\n"), start=1):
        if len(line) > 80:
            issues.append({
                "line": i,
                "type": "style",
                "issue": "Line exceeds 80 characters",
                "severity": "low"
            })

    # Example check: unused import
    if "import" in code and "unused" in code:
        issues.append({
            "line": 1,
            "type": "warning",
            "issue": "Unused import detected",
            "severity": "medium"
        })

    # Example check: missing docstrings
    if "def " in code and '"""' not in code:
        issues.append({
            "line": 1,
            "type": "style",
            "issue": "Missing docstring in function",
            "severity": "medium"
        })

    return issues
