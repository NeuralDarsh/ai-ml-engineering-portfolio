# Data Quality Engineering: Comparing two dictionary schemas to detect missing keys and data type drift

def compare_schema_deltas(baseline_schema, target_schema, parent_key=""):
    """
    Recursively compares a target data dictionary against a baseline schema.
    Flags missing keys, new keys, and structural data type mismatches.
    """
    differences = {
        "missing_keys": [],
        "added_keys": [],
        "type_mismatches": []
    }
    
    baseline_keys = set(baseline_schema.keys())
    target_keys = set(target_schema.keys())
    
    # 1. Identify missing and newly added keys
    for key in baseline_keys - target_keys:
        full_key = f"{parent_key}.{key}" if parent_key else key
        differences["missing_keys"].append(full_key)
        
    for key in target_keys - baseline_keys:
        full_key = f"{parent_key}.{key}" if parent_key else key
        differences["added_keys"].append(full_key)
        
    # 2. Check for type mismatches on overlapping keys
    common_keys = baseline_keys & target_keys
    for key in common_keys:
        full_key = f"{parent_key}.{key}" if parent_key else key
        base_val = baseline_schema[key]
        target_val = target_schema[key]
        
        # If both are nested dictionaries, compare recursively
        if isinstance(base_val, dict) and isinstance(target_val, dict):
            nested_diffs = compare_schema_deltas(base_val, target_val, parent_key=full_key)
            differences["missing_keys"].extend(nested_diffs["missing_keys"])
            differences["added_keys"].extend(nested_diffs["added_keys"])
            differences["type_mismatches"].extend(nested_diffs["type_mismatches"])
        else:
            # Type comparison
            if type(base_val) != type(target_val):
                differences["type_mismatches"].append({
                    "key": full_key,
                    "expected_type": type(base_val).__name__,
                    "actual_type": type(target_val).__name__
                })
                
    return differences

if __name__ == "__main__":
    print("--- Data Engineering: Schema Difference & Drift Auditor ---\n")
    
    # Baseline expected API response schema (v1.0)
    baseline_api_schema = {
        "user_id": 101,
        "username": "darshan_dev",
        "is_active": True,
        "metrics": {
            "score": 98.5,
            "login_count": 42
        }
    }
    
    # Inbound target API response with schema drift (v2.0)
    # (Missing 'is_active', added 'role', type mismatch on 'login_count')
    target_api_schema = {
        "user_id": 101,
        "username": "darshan_dev",
        "role": "admin", # Added key
        "metrics": {
            "score": 98.5,
            "login_count": "42" # Type mismatch: string instead of int
        }
    }
    
    deltas = compare_schema_deltas(baseline_api_schema, target_api_schema)
    
    print("Schema Comparison Audit Report:")
    print("=" * 60)
    print(f" Missing Keys     : {deltas['missing_keys'] or 'None'}")
    print(f" Added Keys       : {deltas['added_keys'] or 'None'}")
    print(f" Type Mismatches  : {deltas['type_mismatches'] or 'None'}")
    print("=" * 60)