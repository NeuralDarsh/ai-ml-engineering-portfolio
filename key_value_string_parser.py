# Developer Tooling: Parsing delimited key-value strings into structured Python dictionaries

import json

def parse_key_value_string(raw_kv_string, pair_delimiter=";", kv_delimiter="="):
    """
    Parses a raw delimited string into a clean dictionary by splitting on pair and key-value delimiters.
    Handles extra whitespace and strips invalid or trailing entries gracefully.
    """
    print("--- Developer Tools: Key-Value String Parser ---")
    print(f"Ingested Raw String: '{raw_kv_string}'\n")
    
    if not raw_kv_string or not raw_kv_string.strip():
        print(" Error: Input string is empty.")
        return {}
        
    parsed_dictionary = {}
    raw_pairs = raw_kv_string.split(pair_delimiter)
    
    for pair in raw_pairs:
        cleaned_pair = pair.strip()
        if not cleaned_pair:
            continue # Skip trailing empty splits
            
        if kv_delimiter in cleaned_pair:
            key, val = cleaned_pair.split(kv_delimiter, 1)
            parsed_dictionary[key.strip()] = val.strip()
        else:
            # Handle flags or keys without explicit values (set value to True)
            parsed_dictionary[cleaned_pair] = True
            
    print(" Deserialized Payload Report:")
    print(" Splitting & Parsing Successful!")
    print(" Formatted JSON Output:")
    print(json.dumps(parsed_dictionary, indent=4))
    print("\n")
    
    return parsed_dictionary

if __name__ == "__main__":
    # Case A: Standard cookie / header-style string separated by semicolons and equals signs
    sample_header_str = "theme=dark; user_id=101; session_token=abc123xyz; secure_flag"
    parse_key_value_string(sample_header_str, pair_delimiter=";", kv_delimiter="=")
    
    print("=" * 60 + "\n")
    
    # Case B: Custom log string separated by pipes and colons
    sample_log_str = "app:SentiAnalyze | env:production | status:ok | version:2.1.0"
    parse_key_value_string(sample_log_str, pair_delimiter="|", kv_delimiter=":")