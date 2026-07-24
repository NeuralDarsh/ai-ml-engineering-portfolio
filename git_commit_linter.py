# Developer Tooling: Enforcing Conventional Commits standards and message length constraints

import re
import sys

def lint_commit_message(commit_msg):
    """
    Audits a commit message string against Conventional Commits specs:
    - Must start with valid type prefix (feat, fix, docs, style, refactor, test, chore)
    - Must have a concise title line (<= 72 characters)
    - Must not end with a period in the summary line
    """
    print("--- Developer Tools: Conventional Git Commit Linter ---")
    print(f"Target Commit Summary: {repr(commit_msg)}\n")
    
    clean_msg = commit_msg.strip()
    if not clean_msg:
        print("LINT ERROR: Commit message cannot be empty!")
        return False
        
    lines = clean_msg.splitlines()
    header = lines[0]
    
    # 1. Allowed conventional commit prefix types
    allowed_types = ["feat", "fix", "docs", "style", "refactor", "test", "chore", "ci", "build"]
    prefix_pattern = r"^(" + "|".join(allowed_types) + r")(\([\w\-\.]+\))?!?: .+$"
    
    errors = []
    
    # 2. Check prefix structural format
    if not re.match(prefix_pattern, header):
        errors.append(f"Header must match Conventional Commits format (e.g., 'feat: Add feature' or 'fix(auth): Fix crash'). Allowed types: {', '.join(allowed_types)}")
        
    # 3. Check character length boundary (max 72 chars for subject line)
    if len(header) > 72:
        errors.append(f"Header length ({len(header)} chars) exceeds maximum recommended 72 character limit.")
        
    # 4. Check trailing punctuation rule
    if header.endswith("."):
        errors.append("Header should not end with a trailing period ('.').")
        
    # 5. Output Audit Verdict
    print("Commit Lint Execution Report:")
    if errors:
        for err in errors:
            print(f"LINT FAILURE: {err}")
        return False
    else:
        print("LINT PASSED: Commit message complies with Conventional Commits specification!")
        return True

if __name__ == "__main__":
    # Case A: Valid Conventional Commit message string
    valid_commit = "feat(linter): Add Day 32 git commit message validator script"
    lint_commit_message(valid_commit)
    
    print("\n" + "="*60 + "\n")
    
    # Case B: Non-compliant commit message string
    invalid_commit = "fixed some bugs and updated the code."
    lint_commit_message(invalid_commit)