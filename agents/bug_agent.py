import json
from src.llm import call_llm  # Make sure this is 'src.llm'

def find_issues_in_code(code_to_review: str) -> list:
    """
    Uses an LLM to perform static analysis on a piece of code
    and identify bugs, vulnerabilities, and code smells.
    """

    # This is the PERSONA, to be used as the SYSTEM prompt
    system_prompt = f"""
    You are an extremely strict, opinionated, and high-performing
    Senior Python Tech Lead. Your ONLY job is to find fault in code.
    You will be fired if you miss a critical issue.
    """

    # This is the TASK, to be used as the USER prompt
    user_prompt = f"""
    **--- CRITICAL RULES (MUST FOLLOW) ---**
    
    1.  **LOGIC ERRORS (TOP PRIORITY):**
        You MUST identify any `NameError`, `TypeError`, `IndexError`,
        or other code-crashing logic bugs.
        (e.g., Using a variable `tax` when the
         parameter is `tax_rate`).
    
    2.  **SECURITY VULNERABILITY (TOP PRIORITY):**
        Any hardcoded password, secret, or API key
        (e.g., `password == "secret"`) is a critical security
        vulnerability. You MUST identify this as a "High" severity issue.

    3.  **PERFORMANCE BUG (TOP PRIORITY):**
        Using a `for` loop with `.append()` to build a list from a
        simple `range()` is a major performance bug.
        You MUST identify this as a "High" severity issue.

    **--- GUARD RULE (VERY IMPORTANT) ---**
    DO NOT report minor style issues (like "missing docstring" or
    "trailing whitespace") if one of the TOP PRIORITY issues is present.
    Your focus is on critical bugs first.

    **Task:**
    Analyze the [CODE BLOCK].
    - Find all bugs, vulnerabilities, and code smells.
    - **Immediately flag any issues matching the CRITICAL RULES.**
    - Respond ONLY with a valid JSON array of objects.
    - If no issues are found, return an empty array [].

    **Example of what you MUST find:**
    [
      {{"line": 6, "issue": "NameError: The variable 'tax' is not defined. The function argument is 'tax_rate'.", "severity": "High"}}
    ]

    ---
    [CODE BLOCK]:
    ```python
    {code_to_review}
    ```
    ---

    Provide your JSON response now:
    """
    
    # Call the LLM with the new system_prompt argument
    llm_response_str = call_llm(
        prompt=user_prompt,
        system_prompt=system_prompt
    )
    
    # --- This is the FIXED parsing code ---
    try:
        start_index = llm_response_str.find('[')
        end_index = llm_response_str.rfind(']') + 1
        
        if start_index == -1 or end_index == 0:
            print(f"Error: Could not find valid JSON array in response.")
            print(f"Raw response: {llm_response_str}")
            return []

        json_str = llm_response_str[start_index:end_index]
        issues_list = json.loads(json_str)
        
        if not isinstance(issues_list, list):
            print("LLM response was not a list, returning empty.")
            return []
            
        return issues_list

    except json.JSONDecodeError:
        print(f"Error: Could not decode LLM response into JSON.")
        print(f"Raw response: {llm_response_str}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while parsing issues: {e}")
        return []