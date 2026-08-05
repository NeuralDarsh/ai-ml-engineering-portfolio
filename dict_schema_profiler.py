# Data Engineering: Recursively profiling Python dictionaries to auto-generate structural schema maps

import json

def profile_dictionary_schema(data_dict):
    """
    Recursively inspects a Python dictionary payload and maps out 
    the structural data schema, key names, and underlying data types.
    """
    schema_map = {}
    
    for key, val in data_dict.items():
        if isinstance(val, dict):
            # Recursively profile nested sub-dictionaries
            schema_map[key] = {
                "type": "Object",
                "properties": profile_dictionary_schema(val)
            }
        elif isinstance(val, list):
            # Inspect list elements to determine array item type
            item_type = type(val[0]).__name__ if val else "unknown"
            schema_map[key] = {
                "type": "Array",
                "item_type": item_type,
                "length": len(val)
            }
        else:
            schema_map[key] = {
                "type": type(val).__name__,
                "sample_value": val
            }
            
    return schema_map

if __name__ == "__main__":
    print("--- Data Engineering: Dictionary Schema Profiler ---")
    
    # Ingest a sample complex API payload
    sample_api_payload = {
        "event_id": "evt_998877",
        "status_code": 200,
        "is_successful": True,
        "latency_ms": 14.5,
        "tags": ["ai", "nlp", "python"],
        "metadata": {
            "environment": "production",
            "region": "ap-south-1",
            "retry_count": 0
        }
    }
    
    print("Ingested Payload Data:\n", json.dumps(sample_api_payload, indent=2), "\n")
    
    # Generate structural schema map
    generated_schema = profile_dictionary_schema(sample_api_payload)
    
    print("Auto-Generated Structural Schema Profile:")
    print("=" * 60)
    print(json.dumps(generated_schema, indent=4))
    print("=" * 60)