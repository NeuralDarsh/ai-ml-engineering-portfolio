# Developer Automation: Extracting and auditing markdown text hyperlinked connection routes

import urllib.request
import urllib.error
import re
import os

def audit_markdown_hyperlinks(target_file_path):
    """
    Parses a markdown layout document to isolate all external hyperlinks, 
    sends fast verification head-pings, and generates a data integrity verdict.
    """
    print("--- Developer Tools: Automated Markdown Link Validator ---")
    print(f"Auditing File Asset: {os.path.basename(target_file_path)}\n")
    
    if not os.path.exists(target_file_path):
        print(" Access Error: The target document path does not exist.")
        return False
        
    # 1. Read string content array from markdown asset
    with open(target_file_path, "r", encoding="utf-8") as f:
        document_text = f.read()
        
    # 2. Extract standard markdown hyperlinks [Text Label](http://example.com) using regex
    markdown_link_pattern = r"\[.*?\]\((https?://.*?)\)"
    extracted_urls = re.findall(markdown_link_pattern, document_text)
    
    # Drop duplicates to keep network scanning efficient
    unique_urls = list(set(extracted_urls))
    
    print(f"Extraction Phase: Found {len(unique_urls)} unique external targets.")
    
    # 3. Connect to each endpoint using optimized HTTP HEAD request streams
    for url in unique_urls:
        print(f" Verifying: {url}")
        
        # Build request with custom user agent headers to skip server firewalls
        request_wrapper = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'},
            method='HEAD'
        )
        
        try:
            # Send light request packet with 3-second timeout guardrail
            with urllib.request.urlopen(request_wrapper, timeout=3.0) as connection:
                status = connection.getcode()
                print(f"ACCESSIBLE | Status Code: {status}")
        except urllib.error.HTTPError as err:
            print(f"DEGRADED | HTTP Error Intercepted: {err.code}")
        except Exception as general_err:
            print(f"BROKEN | Network Target Unreachable: {general_err}")
            
    print("\n Markdown Hyperlink Evaluation Cycle Finished.")
    return True

if __name__ == "__main__":
    # Point directly to your active local workspace README document layout file
    local_readme_path = os.path.join(os.getcwd(), "README.md")
    
    # Check if a local README exists before executing, else fall back to a testing scenario
    if os.path.exists(local_readme_path):
        audit_markdown_hyperlinks(local_readme_path)
    else:
        # Fallback inline test string mock simulation if script runs independently
        print("README.md not found in context. Running sample text validation step...")
        sample_md_file = "temp_test_links.md"
        with open(sample_md_file, "w", encoding="utf-8") as tf:
            tf.write("# Test\nLink A: [GitHub](https://github.com)\nLink B: [Broken Route](https://invalid.endpoint.test-fail)")
        audit_markdown_hyperlinks(sample_md_file)
        if os.path.exists(sample_md_file):
            os.remove(sample_md_file)