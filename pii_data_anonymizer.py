# Security & Data Engineering: Masking and hashing Personally Identifiable Information (PII) in structured payloads

import hashlib
import json
import re

class PIIDataAnonymizer:
    """
    Anonymizes sensitive Personally Identifiable Information (PII)
    in structured dictionaries using masking, salted hashing, and token replacement.
    """
    def __init__(self, salt="portfolio_secure_salt"):
        self.salt = salt

    def _hash_value(self, value):
        """Generates a reproducible, salted SHA-256 hash substring."""
        hasher = hashlib.sha256(f"{self.salt}_{value}".encode("utf-8"))
        return f"anon_user_{hasher.hexdigest()[:10]}"

    def _mask_email(self, email):
        """Masks username part of email: user@example.com -> u***r@example.com"""
        if "@" not in email:
            return "masked_email@example.com"
        user, domain = email.split("@", 1)
        if len(user) <= 2:
            masked_user = user[0] + "*"
        else:
            masked_user = user[0] + "*" * (len(user) - 2) + user[-1]
        return f"{masked_user}@{domain}"

    def _mask_ip(self, ip_address):
        """Masks last two octets of an IPv4 address: 192.168.1.45 -> 192.168.XXX.XXX"""
        parts = ip_address.split(".")
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.XXX.XXX"
        return "XXX.XXX.XXX.XXX"

    def anonymize_payload(self, record):
        """Recursively parses a dictionary and anonymizes recognized PII fields."""
        sanitized = {}
        for key, val in record.items():
            k_lower = key.lower()
            if isinstance(val, dict):
                sanitized[key] = self.anonymize_payload(val)
            elif isinstance(val, list):
                sanitized[key] = [
                    self.anonymize_payload(item) if isinstance(item, dict) else item
                    for item in val
                ]
            elif "email" in k_lower and isinstance(val, str):
                sanitized[key] = self._mask_email(val)
            elif any(tag in k_lower for tag in ["name", "username", "full_name"]) and isinstance(val, str):
                sanitized[key] = self._hash_value(val)
            elif "ip" in k_lower and isinstance(val, str):
                sanitized[key] = self._mask_ip(val)
            elif "phone" in k_lower and isinstance(val, str):
                sanitized[key] = re.sub(r"\d(?=\d{4})", "*", val)
            else:
                sanitized[key] = val
        return sanitized

if __name__ == "__main__":
    print("--- Security Engineering: PII Data Anonymizer ---")
    
    anonymizer = PIIDataAnonymizer()
    
    # Simulated production database record with sensitive user metadata
    raw_user_record = {
        "user_id": 10582,
        "full_name": "Darshan Bagale",
        "email": "darshan.dev@example.com",
        "phone": "+91-9876543210",
        "ip_address": "192.168.1.104",
        "account_metadata": {
            "created_at": "2026-08-18",
            "tier": "enterprise",
            "reviewer_name": "Admin Supervisor"
        }
    }
    
    print("Original Raw Record:")
    print(json.dumps(raw_user_record, indent=4))
    
    anonymized_record = anonymizer.anonymize_payload(raw_user_record)
    
    print("\nAnonymized & Sanitized Record:")
    print(json.dumps(anonymized_record, indent=4))
    print("\nANONYMIZATION COMPLETE: Sensitive PII masked and hashed safely.")