# Developer Automation: Scanning raw text payloads to automatically redact sensitive user information

import re

def sanitize_pii_content(raw_text):
    """
    Scans input text and redacts emails, phone numbers, credit card numbers,
    and IP addresses with standardized privacy masks ([REDACTED_*]).
    """
    print("--- Data Protection: PII Data Sanitizer & Redactor ---")
    print(f"Raw Input Text Stream:\n  {raw_text}\n")
    
    # 1. Define regular expression patterns for standard PII data types
    pii_patterns = {
        "[REDACTED_EMAIL]": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "[REDACTED_PHONE]": r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
        "[REDACTED_IP]": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        "[REDACTED_CARD]": r"\b(?:\d{4}[-\s]?){3}\d{4}\b"
    }
    
    sanitized_text = raw_text
    redaction_counts = {}
    
    # 2. Iterate through patterns and apply regex replacements
    for mask_tag, pattern in pii_patterns.items():
        matches = re.findall(pattern, sanitized_text)
        if matches:
            redaction_counts[mask_tag] = len(matches)
            sanitized_text = re.sub(pattern, mask_tag, sanitized_text)
            
    print("Sanitization Execution Report:")
    if redaction_counts:
        for tag, count in redaction_counts.items():
            print(f"Masked {count} instance(s) of {tag}")
    else:
        print("CLEAN TEXT: No sensitive PII patterns intercepted.")
        
    print(f"\nProtected Text Payload:\n  {sanitized_text}")
    return sanitized_text

if __name__ == "__main__":
    # Simulated incoming support ticket text containing mixed sensitive user entries
    sample_raw_user_ticket = (
        "User reported issue from ip 192.168.1.105. "
        "Contact email is darshan.test@example.com and phone is 987-654-3210. "
        "Payment attempt logged with card 4111-2222-3333-4444."
    )
    
    sanitize_pii_content(sample_raw_user_ticket)