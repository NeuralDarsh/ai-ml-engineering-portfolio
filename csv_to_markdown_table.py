# Developer Automation: Parsing raw CSV text into aligned GitHub-flavored markdown tables

import csv
import io

def convert_csv_to_markdown(raw_csv_text):
    """
    Parses a raw CSV string, computes maximum column widths, 
    and outputs a formatted GitHub Markdown table.
    """
    print("--- Developer Tools: CSV to Markdown Table Converter ---\n")
    
    # 1. Parse CSV string data using standard csv module
    csv_reader = csv.reader(io.StringIO(raw_csv_text.strip()))
    rows = list(csv_reader)
    
    if not rows:
        print("Error: Empty CSV content provided.")
        return ""
        
    headers = rows[0]
    data_rows = rows[1:]
    
    # 2. Calculate maximum width required for each column for dynamic alignment
    col_widths = [len(header) for header in headers]
    for row in data_rows:
        for i, val in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(val))
                
    # 3. Construct header row with padded spacing
    header_line = "| " + " | ".join(headers[i].ljust(col_widths[i]) for i in range(len(headers))) + " |"
    
    # 4. Construct separator row (| :--- | :--- |)
    separator_line = "| " + " | ".join("-" * col_widths[i] for i in range(len(headers))) + " |"
    
    # 5. Construct data rows
    markdown_rows = [header_line, separator_line]
    for row in data_rows:
        formatted_row = "| " + " | ".join(row[i].ljust(col_widths[i]) if i < len(row) else "".ljust(col_widths[i]) for i in range(len(headers))) + " |"
        markdown_rows.append(formatted_row)
        
    final_markdown_table = "\n".join(markdown_rows)
    
    print("Formatted Markdown Table Result:\n")
    print(final_markdown_table)
    return final_markdown_table

if __name__ == "__main__":
    # Simulated raw CSV dataset (e.g., AI model performance benchmarks)
    sample_csv_data = """Model Name, Accuracy, Latency (ms), Deployment Status
GPT-4o-Mini, 98.5%, 45ms, Production Ready
Llama-3-8B, 94.2%, 28ms, Evaluation
BERT-Base, 91.0%, 12ms, Deprecated"""

    convert_csv_to_markdown(sample_csv_data)