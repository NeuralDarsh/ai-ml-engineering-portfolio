# Implementing modulo-arithmetic validation frames to detect hardware transmission corruption

def validate_packet_checksum(payload_bytes, transmitted_checksum):
    """
    Computes a 1-byte checksum from a list of integer payload values.
    Formula: Checksum = Sum(Bytes) % 256
    Compares local hash against the device-transmitted frame header to verify data integrity.
    """
    print("--- IoT Data Gateway: Packet Checksum Validator ---")
    print(f"Incoming Ingestion Payload : {payload_bytes}")
    print(f"Header Checksum Frame Tag  : {transmitted_checksum}\n")
    
    # 1. Structural Validation: Ensure data components are valid byte integers
    if not all(0 <= b <= 255 for b in payload_bytes):
        print("   HARDWARE REJECTION: Payload contains invalid byte range values.")
        return False
        
    # 2. Compute the Modulo Arithmetic Checksum
    total_byte_sum = sum(payload_bytes)
    calculated_checksum = total_byte_sum % 256
    
    print(f" Integrity Calculations Log:")
    print(f" Total Payload Accumulation: {total_byte_sum}")
    print(f"  Gateway Calculated Hash  : {calculated_checksum}")
    
    # 3. Gatekeeper Comparison Matrix Router
    if calculated_checksum == transmitted_checksum:
        print("  INTEGRITY VERIFIED: Packet data matches frame header. Routing payload to AI storage.")
        return True
    else:
        print("  CRITICAL CORRUPTION: Checksum mismatch! Packet drop triggered. Requesting hardware retransmit.")
        return False

if __name__ == "__main__":
    # Case A: Valid hardware stream packet tracking (e.g., [DeviceID, Temp, Humidity, Status])
    stable_sensor_stream = [10, 24, 65, 1]
    expected_hash_A = 100  # (10 + 24 + 65 + 1) = 100 % 256 = 100
    validate_packet_checksum(stable_sensor_stream, expected_hash_A)
    print("\n" + "="*50 + "\n")
    
    # Case B: Corrupted network stream packet tracking (altered payload data due to noise)
    corrupted_sensor_stream = [10, 99, 65, 1] # Temp byte corrupted from 24 to 99
    expected_hash_B = 100 # Heading element still expects the uncorrupted sum
    validate_packet_checksum(corrupted_sensor_stream, expected_hash_B)