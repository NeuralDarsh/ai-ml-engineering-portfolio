# Data Engineering: Measuring JSON serialization footprint and auditing gzip compression efficiency

import json
import gzip

def audit_json_compression(data_payload):
    """
    Serializes a Python dictionary to JSON, measures raw byte size,
    compresses the payload using gzip, and computes compression efficiency.
    """
    print("--- Data Engineering: JSON Compression Auditor ---")
    
    # 1. Serialize dictionary to a clean JSON string and encode to UTF-8 bytes
    json_str = json.dumps(data_payload, indent=None)
    raw_bytes = json_str.encode("utf-8")
    raw_size_bytes = len(raw_bytes)
    
    # 2. Compress payload bytes using gzip compression
    compressed_bytes = gzip.compress(raw_bytes)
    compressed_size_bytes = len(compressed_bytes)
    
    # 3. Calculate reduction savings ratio percentage
    savings_bytes = raw_size_bytes - compressed_size_bytes
    compression_ratio = (compressed_size_bytes / raw_size_bytes) * 100 if raw_size_bytes > 0 else 0
    efficiency_percentage = 100 - compression_ratio
    
    print("Payload Compression Audit Report:")
    print(f" Raw JSON Size      : {raw_size_bytes:,} bytes")
    print(f" Compressed Size    : {compressed_size_bytes:,} bytes")
    print(f" Space Saved        : {savings_bytes:,} bytes ({efficiency_percentage:.1f}% reduction)\n")
    
    if efficiency_percentage > 50:
        print(" HIGH EFFICIENCY: Payload compresses exceptionally well.")
    else:
        print(" MODERATE EFFICIENCY: Payload size is compact.")
        
    return {
        "raw_bytes": raw_size_bytes,
        "compressed_bytes": compressed_size_bytes,
        "efficiency_pct": round(efficiency_percentage, 2)
    }

if __name__ == "__main__":
    # Simulated bulky AI microservice telemetry JSON payload
    sample_telemetry_payload = {
        "batch_id": "batch_99887766_ai",
        "model_engine": "gpt-4o-mini-v1",
        "execution_successful": True,
        "inference_logs": [
            {"token_id": i, "token_text": f"word_token_{i}", "attention_score": 0.992}
            for i in range(100) # Creates repetitive structural data ideal for compression testing
        ]
    }
    
    audit_json_compression(sample_telemetry_payload)