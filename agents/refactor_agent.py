import json
from src.llm import call_llm

def refactor_code(original_code: str, issues_list: list, language: str = "Python") -> str:
    """
    Uses an LLM to refactor the original code based on a list of issues.
    Supports multiple programming languages.
    """

    issues_str = json.dumps(issues_list, indent=2)

    # Language specific best practices
    language_best_practices = {
        "Python": """
        - Use os.environ.get() for environment variables
        - Use f-strings for string formatting
        - Use enumerate() instead of range(len())
        - Handle None checks before accessing attributes
        - Use try/except for error handling
        - Follow PEP 8 style guidelines
        """,
        "Java": """
        - Use System.getenv() for environment variables
        - Use Optional<> to handle null values
        - Use try-with-resources for auto-closing
        - Add null checks before object access
        - Use StringBuilder for string concatenation
        - Follow Java naming conventions
        """,
        "JavaScript": """
        - Use process.env for environment variables
        - Use const/let instead of var
        - Use === instead of == for comparisons
        - Use async/await with try/catch
        - Use optional chaining (?.) for null checks
        - Handle Promise rejections properly
        """,
        "TypeScript": """
        - Use process.env for environment variables
        - Define proper interfaces and types
        - Use optional chaining (?.) for null checks
        - Use type guards for type narrowing
        - Avoid using 'any' type
        - Handle null/undefined explicitly
        """,
        "C++": """
        - Use smart pointers (unique_ptr, shared_ptr)
        - Check pointer validity before dereferencing
        - Use RAII for resource management
        - Use std::string instead of char arrays
        - Add bounds checking for arrays
        - Use const references where appropriate
        """,
        "C#": """
        - Use Environment.GetEnvironmentVariable() for secrets
        - Use null-conditional operator (?.) for null checks
        - Use using statements for IDisposable objects
        - Use string interpolation ($"") for formatting
        - Handle exceptions with try/catch/finally
        - Use async/await for asynchronous operations
        """,
        "Go": """
        - Use os.Getenv() for environment variables
        - Always handle error return values
        - Use defer for cleanup operations
        - Check for nil before dereferencing pointers
        - Use goroutines safely with proper synchronization
        - Follow Go naming conventions
        """,
        "Ruby": """
        - Use ENV[] for environment variables
        - Use safe navigation operator (&.) for nil checks
        - Use rescue for error handling
        - Use frozen_string_literal for string safety
        - Follow Ruby naming conventions
        """,
        "Shell": """
        - Quote all variables "$variable"
        - Use set -e for error handling
        - Check command exit codes
        - Use $() instead of backticks
        - Validate user inputs
        - Use local variables in functions
        """,
        "Rust": """
        - Use std::env::var() for environment variables
        - Handle Result and Option properly with match
        - Avoid unwrap() - use expect() or proper error handling
        - Use references instead of cloning where possible
        - Follow Rust ownership rules
        """
    }

    # Get language specific practices
    best_practices = language_best_practices.get(language, """
        - Use environment variables for secrets
        - Add null/none checks before access
        - Handle errors properly
        - Follow language best practices
    """)

    # Language specific code fence for cleaning response
    language_fences = {
        "Python": ["```python", "```"],
        "Java": ["```java", "```"],
        "JavaScript": ["```javascript", "```", "```js"],
        "TypeScript": ["```typescript", "```", "```ts"],
        "C++": ["```cpp", "```", "```c++"],
        "C": ["```c", "```"],
        "C#": ["```csharp", "```", "```cs"],
        "Go": ["```go", "```"],
        "Ruby": ["```ruby", "```", "```rb"],
        "Shell": ["```bash", "```", "```sh", "```shell"],
        "Rust": ["```rust", "```", "```rs"]
    }

    system_prompt = f"""
    You are an expert senior {language} software engineer. 
    Your task is to refactor the given {language} code 
    to fix all listed issues.
    
    ABSOLUTE RULES:
    1. Fix ALL bugs, security vulnerabilities, and code smells
    2. Do NOT add any new functionality
    3. Do NOT add explanatory comments
    4. Respond ONLY with complete refactored {language} code
    5. CRITICAL: Output MUST be in {language} — never translate 
       to another programming language
    6. If input is {language}, output MUST be {language}
    
    {language} BEST PRACTICES TO APPLY:
    {best_practices}
    """

    user_prompt = f"""
    ---
    [ISSUES REPORT]:
    {issues_str}
    ---
    [{language} ORIGINAL CODE]:
    {original_code}
    ---
    Provide the complete refactored {language} code now.
    Remember: Output MUST be in {language} only.
    """

    llm_response = call_llm(
        prompt=user_prompt,
        system_prompt=system_prompt
    )

    # Clean response — remove all possible code fences
    refactored = llm_response

    # Remove all language specific fences
    fences = language_fences.get(language, ["```"])
    for fence in fences:
        refactored = refactored.replace(fence, "")

    # Clean any remaining generic fences
    refactored = refactored.replace("```python", "")
    refactored = refactored.replace("```java", "")
    refactored = refactored.replace("```javascript", "")
    refactored = refactored.replace("```typescript", "")
    refactored = refactored.replace("```cpp", "")
    refactored = refactored.replace("```csharp", "")
    refactored = refactored.replace("```go", "")
    refactored = refactored.replace("```ruby", "")
    refactored = refactored.replace("```bash", "")
    refactored = refactored.replace("```rust", "")
    refactored = refactored.replace("```", "")
    refactored = refactored.strip()

    return refactored
