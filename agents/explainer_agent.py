import json
from src.llm import call_llm

def explain_changes(original: str, refactored: str, 
                    issues: list, language: str = "Python") -> str:
    """
    Uses an LLM to generate a beginner-friendly explanation of the
    changes between the original and refactored code.
    Supports multiple programming languages.
    """

    issues_str = "\n".join(
        [f"- Line {issue['line']}: {issue['issue']} (severity: {issue['severity']})" 
         for issue in issues]
    ) if issues else "No critical issues found — code was already well-structured."

    # Language specific terminology
    language_context = {
        "Python": {
            "null": "None",
            "exception": "Exception",
            "method": "function",
            "attribute": "attribute",
            "package": "module",
            "secret_fix": "os.environ.get()",
            "null_fix": "if variable is not None"
        },
        "Java": {
            "null": "null",
            "exception": "Exception",
            "method": "method",
            "attribute": "field",
            "package": "package",
            "secret_fix": "System.getenv()",
            "null_fix": "null check or Optional<>"
        },
        "JavaScript": {
            "null": "null/undefined",
            "exception": "Error",
            "method": "function",
            "attribute": "property",
            "package": "module",
            "secret_fix": "process.env",
            "null_fix": "optional chaining (?.) or null check"
        },
        "TypeScript": {
            "null": "null/undefined",
            "exception": "Error",
            "method": "function",
            "attribute": "property",
            "package": "module",
            "secret_fix": "process.env",
            "null_fix": "optional chaining (?.) or type guard"
        },
        "C++": {
            "null": "nullptr",
            "exception": "exception",
            "method": "function",
            "attribute": "member variable",
            "package": "library",
            "secret_fix": "environment variable via getenv()",
            "null_fix": "nullptr check before dereferencing"
        },
        "C#": {
            "null": "null",
            "exception": "Exception",
            "method": "method",
            "attribute": "property",
            "package": "namespace",
            "secret_fix": "Environment.GetEnvironmentVariable()",
            "null_fix": "null-conditional operator (?.) or null check"
        },
        "Go": {
            "null": "nil",
            "exception": "error",
            "method": "function",
            "attribute": "field",
            "package": "package",
            "secret_fix": "os.Getenv()",
            "null_fix": "nil check before dereferencing"
        },
        "Ruby": {
            "null": "nil",
            "exception": "Exception",
            "method": "method",
            "attribute": "attribute",
            "package": "gem",
            "secret_fix": "ENV[]",
            "null_fix": "safe navigation operator (&.) or nil check"
        },
        "Shell": {
            "null": "empty string",
            "exception": "error",
            "method": "function",
            "attribute": "variable",
            "package": "script",
            "secret_fix": "environment variable",
            "null_fix": "variable existence check"
        },
        "Rust": {
            "null": "None",
            "exception": "Error",
            "method": "function",
            "attribute": "field",
            "package": "crate",
            "secret_fix": "std::env::var()",
            "null_fix": "match or if let for Option handling"
        }
    }

    # Get language context or use generic
    ctx = language_context.get(language, {
        "null": "null/none",
        "exception": "error",
        "method": "function",
        "attribute": "property",
        "package": "module",
        "secret_fix": "environment variable",
        "null_fix": "null/none check"
    })

    system_prompt = f"""
    You are a friendly programming tutor at an enterprise 
    software company specializing in {language}.
    Your goal is to explain the difference between original 
    {language} code and its refactored version in a way 
    a beginner can understand.
    Be encouraging and educational, not critical.
    
    IMPORTANT RULES:
    1. Always write a COMPLETE explanation — never stop halfway
    2. Cover every single change made in detail
    3. Always end with a clear Summary section
    4. If no issues were found explain what the code does well
    5. Use simple language a junior {language} developer understands
    6. Reference specific line numbers when explaining changes
    7. Always explain security implications of credential changes
    8. Use {language} specific terminology:
       - Use "{ctx['null']}" not "null/none" generically
       - Use "{ctx['method']}" not "function" generically
       - Use "{ctx['secret_fix']}" as the recommended secret fix
       - Use "{ctx['null_fix']}" as the null safety recommendation
    """

    user_prompt = f"""
    You are reviewing {language} code changes.
    
    Write a COMPLETE educational explanation following this structure:
    
    
    Write a brief friendly introduction mentioning this is {language} code.
    
    ## Summary of Changes
    High level overview of what was fixed and why it matters.
    
    ## Detailed Breakdown
    For each change explain:
    - What was changed (with line number)
    - Why it was changed
    - What {language} best practice it follows
    - What would have happened without the fix
    
    ## Security Improvements
    If any credentials or secrets were fixed explain:
    - Why hardcoded secrets are dangerous in {language} projects
    - How {ctx['secret_fix']} is the correct {language} approach
    - What could happen if deployed with hardcoded secrets
    
    ## What You Learned
    Key {language} best practices from this refactoring:
    - List 3-5 specific {language} lessons
    
    ## Closing
    Encouraging message for the developer.
    
    CRITICAL: Write the COMPLETE explanation. Never stop early.
    
    ---
    [ISSUES REPORT]:
    {issues_str}
    ---
    [{language} ORIGINAL CODE]:
    {original}
    ---
    [{language} REFACTORED CODE]:
    {refactored}
    ---
    Write your complete {language} explanation now:
    """

    explanation = call_llm(
        prompt=user_prompt,
        system_prompt=system_prompt,
        max_tokens=3000
    )

    return explanation
