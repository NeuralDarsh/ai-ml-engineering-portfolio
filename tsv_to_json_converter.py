# Data Engineering: Parsing tab-separated value streams, auto-casting data types, and exporting JSON arrays

import csv
import io
import json

def convert_tsv_to_json(raw_tsv_text):
    """
    Parses a tab-separated values (TSV) string, auto-detects numerical and boolean types,
    and converts the records into a clean list of structured JSON dictionaries.
    """
    print("--- Data Engineering: TSV to Standardized JSON Converter ---")
    
    if not raw_tsv_text or not raw_tsv_text.strip():
        print(" Error: Provided TSV content is empty.")
        return []

    # 1. Read tab-delimited text stream
    reader = csv.reader(io.StringIO(raw_tsv_text.strip()), delimiter='\t')
    rows = list(reader)
    
    if not rows:
        print(" Error: No valid rows found in TSV payload.")
        return []
        
    headers = [h.strip() for h in rows[0]]
    data_rows = rows[1:]
    
    json_records = []
    
    # 2. Iterate through rows and map values to header keys with dynamic type casting
    for row in data_rows:
        if not row:
            continue
            
        record = {}
        for idx, val in enumerate(row):
            if idx < len(headers):
                clean_val = val.strip()
                
                # Dynamic type casting logic
                if clean_val.lower() == "true":
                    typed_val = True
                elif clean_val.lower() == "false":
                    typed_val = False
                elif clean_val.isdigit():
                    typed_val = int(clean_val)
                else:
                    try:
                        typed_val = float(clean_val)
                    except ValueError:
                        typed_val = clean_val
                        
                record[headers[idx]] = typed_val
                
        json_records.append(record)
        
    print("TSV Parsing & Conversion Report:")
    print(f"Extracted Headers : {headers}")
    print(f"Converted Records  : {len(json_records)} rows\n")
    print("Formatted JSON Output Payload:")
    print(json.dumps(json_records, indent=4))
    print("\n")
    
    return json_records

if __name__ == "__main__":
    # Simulated TSV log dataset containing tab characters (\t)
    sample_tsv_payload = (
        "service_id\tlatency_ms\tis_active\trating\n"
        "senti_analyze_pro\t45\ttrue\t4.8\n"
        "auth_microservice\t12\ttrue\t4.9\n"
        "slop_detector_api\t120\tfalse\t4.2"
    )
    
    convert_tsv_to_json(sample_tsv_payload)