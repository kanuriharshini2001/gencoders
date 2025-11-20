import json
from src.llm import call_llm

def explain_changes(original: str, refactored: str, issues: list) -> str:
    """
    Uses an LLM to generate a beginner-friendly explanation of the
    changes between the original and refactored code.
    """
    
    issues_str = "\n".join(
        [f"- Line {issue['line']}: {issue['issue']} (severity: {issue['severity']})" for issue in issues]
    )

    system_prompt = """
    You are a friendly programming tutor. Your goal is to explain the difference
    between a piece of original code and its refactored version in a way
    a beginner can understand. Be encouraging and educational, not critical.
    """

    user_prompt = f"""
    You will be given the [ORIGINAL CODE], the [ISSUES REPORT] found,
    and the final [REFACTORED CODE].

    Your task is to:
    1.  Start with a brief summary of the changes.
    2.  Go through each major change, explaining *what* was changed.
    3.  Explain *why* it was changed, referencing the [ISSUES REPORT].
    4.  Explain the programming "best practice" behind the change.

    ---
    [ISSUES REPORT]:
    {issues_str}

    ---
    [ORIGINAL CODE]:
    ```python
    {original}
    ```

    ---
    [REFACTORED CODE]:
    ```python
    {refactored}
    ```
    ---

    Provide your explanation now:
    """

    explanation = call_llm(
        prompt=user_prompt,
        system_prompt=system_prompt
    )
    
    return explanation