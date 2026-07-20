# Developer Automation: Parsing messy SQL strings into structured, readable database queries

import re

def format_sql_query(raw_query):
    """
    Parses an unformatted SQL string, standardizes reserved keywords to UPPERCASE,
    and applies clean line breaks and indentation.
    """
    print("--- Developer Tools: SQL Query Formatter ---")
    print(f"Raw Input Query:\n  {raw_query}\n")
    
    # 1. Clean up multi-space noise into single space strings
    cleaned_query = re.sub(r'\s+', ' ', raw_query.strip())
    
    # 2. List of standard SQL reserved keywords to standardize
    sql_keywords = [
        "SELECT", "FROM", "WHERE", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN",
        "GROUP BY", "ORDER BY", "HAVING", "LIMIT", "AND", "OR", "ON", "INSERT INTO", "UPDATE", "SET"
    ]
    
    # Major clauses that should start on a fresh new line
    newline_keywords = [
        "SELECT", "FROM", "WHERE", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN",
        "GROUP BY", "ORDER BY", "HAVING", "LIMIT", "SET"
    ]
    
    # 3. Case-insensitive replacement to convert keywords to uppercase
    formatted_text = cleaned_query
    for kw in sql_keywords:
        pattern = re.compile(rf'\b{kw}\b', re.IGNORECASE)
        formatted_text = pattern.sub(kw, formatted_text)
        
    # 4. Insert newlines before major SQL clauses
    for n_kw in newline_keywords:
        pattern = re.compile(rf'\b{n_kw}\b')
        formatted_text = pattern.sub(rf'\n{n_kw}', formatted_text)
        
    # 5. Indent conditions and format commas cleanly
    formatted_lines = []
    for line in formatted_text.strip().split('\n'):
        line = line.strip()
        if any(line.startswith(kw) for kw in newline_keywords):
            formatted_lines.append(line)
        else:
            formatted_lines.append(f"  {line}") # Add 2-space indentation for clauses
            
    final_sql = "\n".join(formatted_lines)
    
    print("Formatted SQL Result:")
    print(f"----------------------------------------\n{final_sql}\n----------------------------------------")
    return final_sql

if __name__ == "__main__":
    # Simulated messy, unformatted raw SQL query string from code or logs
    messy_sql = "select user_id, username, email from users inner join activity_logs on users.id = activity_logs.user_id where status = 'active' and created_at >= '2026-01-01' order by created_at desc limit 10;"
    
    format_sql_query(messy_sql)