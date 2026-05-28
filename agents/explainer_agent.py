import json
from src.llm import call_llm

def explain_changes(original: str, refactored: str, issues: list) -> str:
    """
    Uses an LLM to generate a beginner-friendly explanation of the
    changes between the original and refactored code.
    """
    
    issues_str = "\n".join(
        [f"- Line {issue['line']}: {issue['issue']} (severity: {issue['severity']})" for issue in issues]
    ) if issues else "No critical issues found — code was already well-structured."

    system_prompt = """
    You are a friendly programming tutor at an enterprise software company.
    Your goal is to explain the difference between a piece of original code 
    and its refactored version in a way a beginner can understand.
    Be encouraging and educational, not critical.
    
    IMPORTANT RULES:
    1. Always write a COMPLETE explanation — never stop halfway
    2. Cover every single change made in detail
    3. Always end with a clear "Summary" section
    4. If no issues were found, explain what the code does well
    5. Use simple language a junior developer can understand
    6. Reference specific line numbers when explaining changes
    7. Always explain the security implications of any credential changes
    """

    user_prompt = f"""
    You will be given the [ORIGINAL CODE], the [ISSUES REPORT] found,
    and the final [REFACTORED CODE].
    
    Your task is to write a COMPLETE educational explanation:
    
    1. Start with "## AI-Generated Documentation"
    2. Write a brief friendly introduction
    3. Write "## Summary of Changes" section
    4. Write "## Detailed Breakdown" section covering each change:
       - What was changed
       - Why it was changed
       - What best practice it follows
       - What would have happened without the fix
    5. Write "## Security Improvements" section if credentials were fixed
    6. Write "## What You Learned" section with key takeaways
    7. End with an encouraging closing message
    
    CRITICAL: Write the COMPLETE explanation. Do not stop early.
    
    ---
    [ISSUES REPORT]:
    {issues_str}
    ---
    [ORIGINAL CODE]:
    {original}
    ---
    [REFACTORED CODE]:
    {refactored}
    ---
    Write your complete explanation now:
    """

    explanation = call_llm(
        prompt=user_prompt,
        system_prompt=system_prompt,
        max_tokens=3000
    )
    
    return explanation
