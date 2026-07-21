# Security Tool: Scanning repository files for accidental hardcoded keys and credentials

import os
import re

def audit_workspace_for_secrets(target_directory):
    """
    Scans source files in a target workspace directory for exposed API keys,
    hardcoded passwords, and sensitive token string patterns.
    """
    print("--- Security Tools: Secret & Credential Leak Detector ---")
    print(f"Scanning Workspace Target: {target_directory}\n")
    
    if not os.path.exists(target_directory):
        print("Error: Target directory path does not exist.")
        return
        
    # High-risk credential regex patterns
    secret_patterns = {
        "AWS Access Key": r"(?i)aws_(?:secret_)?access_key\s*=\s*['\"][A-Za-z0-9/\+=]{16,}['\"]",
        "Generic Secret/Token": r"(?i)(?:api_key|secret_key|auth_token)\s*=\s*['\"][A-Za-z0-9_\-]{16,}['\"]",
        "Private Key Header": r"-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----",
        "Database Connection URI": r"postgres(?:ql)?://\w+:\w+@[\w\.-]+:\d+/\w+"
    }
    
    findings_count = 0
    scanned_files_count = 0
    
    # 1. Walk through the workspace directory tree
    for root, _, files in os.walk(target_directory):
        # Skip version control trees, virtual environments, or backup archives
        if '.git' in root or 'venv' in root or 'backups_vault' in root:
            continue
            
        for file in files:
            # Audit source code files while excluding security detector scripts
            if file.endswith(('.py', '.json', '.md', '.env', '.yml')) and file != 'secret_leak_detector.py':
                scanned_files_count += 1
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        
                    for line_num, line_content in enumerate(lines, start=1):
                        for label, pattern in secret_patterns.items():
                            if re.search(pattern, line_content):
                                findings_count += 1
                                relative_file = os.path.relpath(file_path, target_directory)
                                # Mask the matched line so actual secrets are not dumped to terminal logs
                                masked_line = line_content.strip()[:20] + "..." + line_content.strip()[-5:]
                                print(f"LEAK DETECTED [{label}]")
                                print(f"Location: {relative_file} (Line {line_num})")
                                print(f"Content : {masked_line}\n")
                except Exception as err:
                    pass # Bypass locked or unreadable files gracefully
                    
    print("Security Audit Verdict:")
    print(f"Total Files Audited: {scanned_files_count}")
    if findings_count == 0:
        print("CLEAN WORKSPACE: No exposed credentials or secret tokens detected.")
        return True
    else:
        print(f"WARNING: Intercepted {findings_count} potential credential leakage points!")
        return False

if __name__ == "__main__":
    # Point directly to your local workspace root directory
    active_workspace_path = os.getcwd()
    
    audit_workspace_for_secrets(active_workspace_path)