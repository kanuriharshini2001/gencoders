import json
from src.llm import call_llm

def find_issues_in_code(code_to_review: str, language: str = "Python") -> list:
    """
    Uses an LLM to perform static analysis on a piece of code
    and identify bugs, vulnerabilities, and code smells.
    Supports multiple programming languages.
    """

    # Language specific rules
    language_rules = {
        "Python": """
        - NameError: undefined variables
        - IndexError: list index out of range
        - TypeError: wrong type operations
        - ZeroDivisionError: division by zero
        - NoneType errors: accessing attributes on None
        - String + integer concatenation
        - range(len(x) + 1) loop boundary errors
        """,
        "Java": """
        - NullPointerException: null object access
        - ArrayIndexOutOfBoundsException: array boundary errors
        - ClassCastException: invalid type casting
        - Resource leaks: unclosed streams/connections
        - Integer division truncation errors
        - Missing null checks
        """,
        "JavaScript": """
        - undefined variable access
        - null reference errors
        - Type coercion bugs (== vs ===)
        - Async/await errors
        - Missing error handling in promises
        - Scope issues with var vs let/const
        """,
        "TypeScript": """
        - Type assertion errors
        - Null/undefined access
        - Interface implementation errors
        - Generic type mismatches
        - Missing null checks
        """,
        "C++": """
        - Null pointer dereference
        - Memory leaks: missing delete/free
        - Buffer overflow
        - Use after free
        - Integer overflow
        - Uninitialized variables
        """,
        "C#": """
        - NullReferenceException
        - IndexOutOfRangeException
        - InvalidCastException
        - Unhandled exceptions
        - Missing using statements for IDisposable
        """,
        "Go": """
        - Nil pointer dereference
        - Goroutine leaks
        - Channel deadlocks
        - Error not handled
        - Race conditions
        """,
        "Ruby": """
        - NoMethodError on nil
        - ArgumentError wrong number of args
        - Missing error handling
        - Undefined variables
        """,
        "Shell": """
        - Unquoted variables
        - Missing error handling
        - Unsafe use of user input
        - Missing exit codes
        """,
        "Rust": """
        - Borrow checker violations
        - Unwrap on None/Err without handling
        - Integer overflow
        - Unsafe block misuse
        """
    }

    # Get language specific rules or use generic
    specific_rules = language_rules.get(language, """
        - Logic errors and crashes
        - Null/None pointer errors
        - Index out of bounds
        - Division by zero
        - Type mismatch errors
    """)

    system_prompt = f"""
    You are an extremely strict, opinionated, and high-performing
    Senior {language} Tech Lead. Your ONLY job is to find fault in code.
    You will be fired if you miss a critical issue.
    You are an expert in {language} programming language specifically.
    """

    user_prompt = f"""
    **--- CRITICAL RULES (MUST FOLLOW) ---**
    
    You are analyzing {language} code. Apply {language} specific rules.
    
    1. **LOGIC ERRORS (TOP PRIORITY):**
       Find any code-crashing bugs specific to {language}:
       {specific_rules}
    
    2. **SECURITY VULNERABILITY (TOP PRIORITY):**
       Any hardcoded password, secret, API key, token,
       database credentials, server addresses
       (e.g., password = "secret123") is a critical 
       security vulnerability.
       You MUST identify this as a "High" severity issue.
    
    3. **PERFORMANCE BUG (TOP PRIORITY):**
       Inefficient loops, unnecessary operations,
       poor data structure choices.
       You MUST identify this as a "High" severity issue.
    
    4. **INJECTION VULNERABILITIES (TOP PRIORITY):**
       SQL injection, command injection, or any
       unsanitized user input used in queries.
       You MUST identify this as a "High" severity issue.

    **--- GUARD RULE (VERY IMPORTANT) ---**
    DO NOT report minor style issues like missing 
    docstrings or trailing whitespace if a TOP PRIORITY 
    issue is present. Focus on critical bugs first.

    **Task:**
    Analyze the [{language} CODE BLOCK].
    - Find all bugs, vulnerabilities, and code smells.
    - Immediately flag any issues matching CRITICAL RULES.
    - Respond ONLY with a valid JSON array of objects.
    - If no issues are found, return an empty array [].
    - Always use {language} terminology in descriptions.

    **Example output format:**
    [
      {{
        "line": 6,
        "issue": "Hardcoded password detected — move to environment variable",
        "severity": "High"
      }},
      {{
        "line": 12,
        "issue": "NullPointerException risk — check for null before accessing",
        "severity": "High"
      }}
    ]

    ---
    [{language} CODE BLOCK]:
    {code_to_review}
    ---
    Provide your JSON response now:
    """

    # Call the LLM
    llm_response_str = call_llm(
        prompt=user_prompt,
        system_prompt=system_prompt
    )

    # Parse JSON response
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
