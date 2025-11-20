import json
from src.llm import call_llm

def refactor_code(original_code: str, issues_list: list) -> str:
    """
    Uses an LLM to refactor the original code based on a list of issues.
    """
    
    issues_str = json.dumps(issues_list, indent=2)

    system_prompt = """
    You are an expert senior software engineer. Your task is to refactor
    the given code to fix all listed issues.
    - You must fix all bugs, security vulnerabilities, and code smells.
    - Do not add any new functionality.
    - Do not add any comments or explanations.
    - Respond ONLY with the complete, refactored Python code block.
    """

    user_prompt = f"""
    ---
    [ISSUES REPORT]:
    {issues_str}

    ---
    [ORIGINAL CODE]:
    ```python
    {original_code}
    ```
    ---

    Provide the refactored code now:
    """

    llm_response = call_llm(
        prompt=user_prompt,
        system_prompt=system_prompt
    )
    
    refactored_code = llm_response.replace("```python", "").replace("```", "").strip()
    
    return refactored_code