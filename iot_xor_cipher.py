# Implementing high-efficiency symmetric bitwise cryptography for resource-constrained edge nodes

def run_xor_cipher(input_string, secret_key_char):
    """
    Applies a bitwise XOR transformation over a text payload using a single-character key.
    Since XOR is symmetric, passing the cipher text back through with the same key decrypts it.
    """
    print("--- IoT Security Core: Symmetric XOR Cipher Pipeline ---")
    print(f"Input Data String   : '{input_string}'")
    print(f"Cryptographic Key   : '{secret_key_char}' (Hex: {hex(ord(secret_key_char))})\n")
    
    # 1. Convert the single key character into its integer byte representation
    key_byte = ord(secret_key_char)
    
    # 2. Perform element-wise bitwise XOR operation via character-to-integer casting
    transformed_chars = []
    for char in input_string:
        # XOR bit-flip logic operator (^) applied between string character byte and key byte
        scrambled_byte = ord(char) ^ key_byte
        transformed_chars.append(chr(scrambled_byte))
        
    output_result = "".join(transformed_chars)
    
    print(" Cryptographic Transformation Log:")
    print(f"  Resulting Output Payload Stream: {repr(output_result)}")
    return output_result

if __name__ == "__main__":
    # Simulated sensitive industrial hardware string data frame packet
    # Contains sensor identifiers, readings, and localization details
    raw_telemetry_payload = "NODE-OSAKA-92:TEMP=24.5C"
    secret_auth_token = "J"  # Cryptographic symmetric key byte string descriptor
    
    # --- PHASE A: ENCRYPTION ---
    print("[Executing Ingestion Phase: Encrypting Raw Text Sensor Stream]")
    encrypted_cipher = run_xor_cipher(raw_telemetry_payload, secret_auth_token)
    
    print("\n" + "="*60 + "\n")
    
    # --- PHASE B: DECRYPTION ---
    print("[Executing Gateway Phase: Decrypting Received Cipher Back to Text]")
    # Re-running the exact same bitwise function restores the original array characters perfectly
    decrypted_payload = run_xor_cipher(encrypted_cipher, secret_auth_token)