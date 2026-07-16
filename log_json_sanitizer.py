# Developer Automation: Parsing unstructured text logs into clean, structured JSON databases

import json
import os
import re
from datetime import datetime

def sanitize_production_logs(raw_log_lines):
    """
    Parses unstructured text log streams, extracts key data points using expressions,
    and returns a structured list of normalized data dictionaries.
    """
    print("--- Data Engineering: Production Log Sanitizer ---\n")
    
    structured_logs = []
    
    # Regular expression pattern to extract: [TIMESTAMP] [LEVEL] [MODULE] Message
    log_pattern = r"\[(.*?)\]\s+([A-Z]+)\s+\s+([\w\.\-]+):\s+(.*)"
    
    for line in raw_log_lines:
        match = re.match(log_pattern, line)
        if match:
            timestamp_str, log_level, module_name, message = match.groups()
            
            # Structure the raw data into a clean database schema object
            log_entry = {
                "timestamp": timestamp_str,
                "level": log_level,
                "module": module_name,
                "message": message.strip(),
                "processed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            structured_logs.append(log_entry)
            print(f" parsed successfully: [{log_level}] from module '{module_name}'")
        else:
            print(f" skipped unparseable line noise: {repr(line)}")
            
    return structured_logs

if __name__ == "__main__":
    # Simulated messy, raw text log file data streams from a runtime server application
    simulated_raw_logs = [
        "[2026-07-16 19:15:02] INFO     auth_service: User login successful for admin.",
        "CRITICAL SYSTEM CORRUPTION WARNING - CORRUPT PACKET INTERCEPTED", # Noise line to strip
        "[2026-07-16 19:15:30] WARNING  database_adapter: Connection pool utilization reached 88%.",
        "[2026-07-16 19:16:12] ERROR    api_gateway: Failed to route requests to international nodes.",
        "--- RUNTIME DEPLOYMENT LOG WINDOW TERMINATED ---" # Another line of noise
    ]
    
    # Process the unstructured string lines
    cleaned_data = sanitize_production_logs(simulated_raw_logs)
    
    # Save the structured data records to a distribution JSON file target
    output_filename = "sanitized_system_logs.json"
    with open(output_filename, "w", encoding="utf-8") as json_file:
        json.dump(cleaned_data, json_file, indent=4)
        
    print(f"\n Export complete! {len(cleaned_data)} structured entries saved to '{output_filename}'.")