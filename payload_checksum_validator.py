# Security & Distributed Systems: Generating and validating SHA-256 payload checksums to prevent data corruption

import hashlib
import json

class PayloadChecksumValidator:
    """
    Computes deterministic SHA-256 digests for structured payloads
    and verifies transmission integrity against incoming checksum headers.
    """
    def generate_checksum(self, payload):
        """
        Serializes dictionary into a deterministic JSON string (sorted keys, no extra spaces)
        and computes its SHA-256 hexadecimal digest.
        """
        canonical_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        payload_bytes = canonical_json.encode('utf-8')
        digest = hashlib.sha256(payload_bytes).hexdigest()
        return digest

    def verify_integrity(self, payload, expected_checksum):
        """
        Compares the calculated checksum of an ingested payload
        against an expected checksum to audit integrity.
        """
        print("--- Systems & Security: Payload Checksum Validator ---")
        computed_checksum = self.generate_checksum(payload)
        
        print(f"Ingested Payload:\n  {json.dumps(payload, indent=2)}")
        print(f" Expected Checksum : {expected_checksum}")
        print(f" Computed Checksum : {computed_checksum}\n")

        if computed_checksum == expected_checksum:
            print(" INTEGRITY VERDICT: PASS (Payload is authentic and uncorrupted)\n")
            return True
        else:
            print(" INTEGRITY VERDICT: FAIL (Payload mismatch / Data tampering detected)\n")
            return False

if __name__ == "_main_":
    validator = PayloadChecksumValidator()

    # 1. Original valid microservice payload
    original_event = {
        "event_id": "tx_99812",
        "sender": "service_auth",
        "amount": 250.0,
        "is_verified": True
    }

    # Generate legitimate checksum
    valid_checksum = validator.generate_checksum(original_event)

    # Test Case A: Verify valid payload transmission
    print("Test Case 1: Valid Inbound Transmission")
    validator.verify_integrity(original_event, valid_checksum)

    print("=" * 60 + "\n")

    # Test Case B: Verify corrupted/tampered payload (e.g. amount modified during transit)
    tampered_event = dict(original_event)
    tampered_event["amount"] = 2500.0  # Modified value

    print("Test Case 2: Corrupted Inbound Transmission")
    validator.verify_integrity(tampered_event, valid_checksum)