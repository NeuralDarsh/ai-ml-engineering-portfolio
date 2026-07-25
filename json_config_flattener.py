# Developer Automation: Recursively flattening nested JSON objects into dot-notation key-value maps

import json

def flatten_json_config(nested_dict, parent_key='', separator='.'):
    """
    Recursively iterates through nested dictionaries and converts multi-level keys
    into flat dot-notation string keys suitable for environment settings.
    """
    items = []
    
    for key, value in nested_dict.items():
        new_key = f"{parent_key}{separator}{key}" if parent_key else key
        
        if isinstance(value, dict):
            # Recursively unpack nested sub-dictionaries
            items.extend(flatten_json_config(value, new_key, separator=separator).items())
        elif isinstance(value, list):
            # Convert lists into indexed flat keys (e.g., "allowed_origins.0")
            for i, elem in enumerate(value):
                if isinstance(elem, dict):
                    items.extend(flatten_json_config(elem, f"{new_key}{separator}{i}", separator=separator).items())
                else:
                    items[f"{new_key}{separator}{i}"] = elem
        else:
            items.append((new_key, value))
            
    return dict(items)

if __name__ == "__main__":
    print("--- Developer Tools: JSON Configuration Flattener ---")
    
    # Simulated complex, multi-level application configuration JSON
    nested_app_config = {
        "app": {
            "name": "SentiAnalyze-Pro",
            "version": "2.1.0",
            "settings": {
                "debug_mode": True,
                "timeout_sec": 30
            }
        },
        "database": {
            "credentials": {
                "host": "127.0.0.1",
                "port": 5432
            }
        },
        "cors": {
            "allowed_origins": ["https://localhost:3000", "https://app.domain.com"]
        }
    }

    print("Original Nested JSON Configuration structure ingested.\n")
    
    # Process flattening transformation
    flat_config = flatten_json_config(nested_app_config)
    
    print("Transformed Flat Configuration Map (Dot-Notation):")
    print("=" * 60)
    for k, v in flat_config.items():
        print(f"  🔹 {k:<35} = {repr(v)}")
    print("=" * 60)