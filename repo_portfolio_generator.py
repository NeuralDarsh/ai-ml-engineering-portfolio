# Developer Tool: Automates directory indexing and metrics tracking for technical portfolios

import os
from datetime import datetime

def generate_repository_summary(target_directory):
    """
    Scans the local repository directory, audits code assets, 
    and automatically builds a structured markdown profile summary report.
    """
    print("--- Developer Tools: Portfolio Profile Auto-Generator ---")
    print(f"Scanning Workspace: {target_directory}\n")
    
    if not os.path.exists(target_directory):
        print(" Error: Target directory path does not exist.")
        return
        
    python_files_count = 0
    total_lines_of_code = 0
    analyzed_modules = []
    
    # 1. Walk through repository filesystem directory tree
    for root, _, files in os.walk(target_directory):
        # Skip hidden git folders or virtual environments
        if '.git' in root or 'venv' in root:
            continue
            
        for file in files:
            if file.endswith('.py') and file != 'repo_portfolio_generator.py':
                python_files_count += 1
                file_path = os.path.join(root, file)
                
                # Count functional production lines of code inside the file
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        total_lines_of_code += len(lines)
                        analyzed_modules.append((file, len(lines)))
                except Exception:
                    pass # Gracefully bypass file read issues if locked
                    
    # 2. Construct the Markdown content string dynamically
    markdown_output = (
        f"#  Automated Engineering Portfolio Manifest\n"
        f"Generated automatically on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"##  Repository Metadata Statistics\n"
        f"- **Total Active Production Modules:** {python_files_count} files\n"
        f"- **Total Codebases Scale:** {total_lines_of_code} lines of code\n\n"
        f"##  Indexed Core Code Assets\n"
        f"| Production Module Name | Size (Lines of Code) |\n"
        f"| :--- | :--- |\n"
    )
    
    for mod_name, mod_lines in analyzed_modules:
        markdown_output += f"| `{mod_name}` | {mod_lines} lines |\n"
        
    # 3. Write data to a separate profile showcase file
    report_filename = "portfolio_manifest.md"
    with open(os.path.join(target_directory, report_filename), "w", encoding="utf-8") as rf:
        rf.write(markdown_output)
        
    print(f" Developer Execution Audit Report Complete:")
    print(f"  Scanned {python_files_count} active development scripts.")
    print(f"  Measured a cumulative {total_lines_of_code} lines of production code.")
    print(f"  Live asset document successfully exported to: {report_filename}")

if __name__ == "__main__":
    # Point directly to your active local repository root path folder
    local_workspace_root = os.getcwd()
    generate_repository_summary(local_workspace_root)