# System Utilities: Parsing human-readable memory size strings into standardized byte metrics

import re

def parse_memory_size_to_bytes(size_str):
    """
    Parses a human-readable memory string (e.g., '16 GB', '512MB', '1.5 TB')
    and converts it into total bytes and normalized megabytes (MB).
    """
    print("--- System Tools: Memory Unit Normalizer ---")
    print(f"Ingested Size String: '{size_str}'\n")
    
    clean_str = size_str.strip().upper()
    
    # 1. Regex pattern to extract numerical value and unit label
    pattern = r"^([\d\.]+)\s*([A-Z]+)?$"
    match = re.match(pattern, clean_str)
    
    if not match:
        print(f"Error: Invalid memory size format: '{size_str}'")
        return None
        
    value_float = float(match.group(1))
    unit = match.group(2) if match.group(2) else "B"
    
    # 2. Binary conversion multipliers relative to Bytes (1 KB = 1024 Bytes)
    unit_multipliers = {
        "B": 1,
        "KB": 1024,
        "MB": 1024 ** 2,
        "GB": 1024 ** 3,
        "TB": 1024 ** 4,
        "PB": 1024 ** 5
    }
    
    if unit not in unit_multipliers:
        print(f"Error: Unsupported unit label '{unit}'. Supported: {list(unit_multipliers.keys())}")
        return None
        
    # 3. Calculate byte metrics
    total_bytes = int(value_float * unit_multipliers[unit])
    normalized_mb = total_bytes / (1024 ** 2)
    
    print("Memory Normalization Report:")
    print(f"Ingested Value   : {value_float} {unit}")
    print(f"Total Bytes      : {total_bytes:,} Bytes")
    print(f"Normalized MB    : {normalized_mb:.2f} MB\n")
    
    return {"bytes": total_bytes, "megabytes": normalized_mb}

if __name__ == "__main__":
    # Test cases with different units and formatting spacing
    test_sizes = ["512MB", "16 GB", "2.5 TB", "1024 KB"]
    
    for size in test_sizes:
        parse_memory_size_to_bytes(size)