# Security & Data Quality Engineering: Applying regular expression rules to redact sensitive patterns in text streams

import re

class RegexPatternMasker:
    """
    Applies configurable Regular Expression substitution rules to mask
    sensitive strings in raw text payloads prior to persistent logging or indexing.
    """
    def __init__(self):
        # Default sensitive pattern mapping: Label -> (Regex Pattern, Replacement Function / Mask)
        self.rules = {
            "Credit Card": (r"\b(?:\d{4}[-\s]?){3}\d{4}\b", lambda m: f"XXXX-XXXX-XXXX-{m.group()[-4:]}"),
            "Social Security / ID": (r"\b\d{3}-\d{2}-\d{4}\b", "***-**-****"),
            "API Secret Token": (r"(?i)(bearer\s+|token:\s*)([a-zA-Z0-9_\-\.]{16,})", r"\1[REDACTED_TOKEN]")
        }

    def mask_text(self, raw_text):
        print("--- Security Engineering: RegEx Pattern Masker ---")
        print(f"Ingested Raw String:\n  {raw_text}\n")

        sanitized_text = raw_text
        for rule_name, (pattern, replacement) in self.rules.items():
            before_text = sanitized_text
            if callable(replacement):
                sanitized_text = re.sub(pattern, replacement, sanitized_text)
            else:
                sanitized_text = re.sub(pattern, replacement, sanitized_text)

            if before_text != sanitized_text:
                print(f"Rule Applied: [{rule_name}] masked sensitive occurrences.")

        print("\nSanitization Summary:")
        print(f"Sanitized Output String:\n  {sanitized_text}\n")
        return sanitized_text

if __name__ == "__main__":
    masker = RegexPatternMasker()

    # Simulated raw application log stream containing sensitive tokens and credentials
    raw_log_payload = (
        "User session initialized. Payment attempted with card 4111-2222-3333-4444. "
        "Identity verification check for SSN 123-45-6789 returned valid. "
        "Authorization header passed: Bearer secret_token_abc123xyz987654."
    )

    masker.mask_text(raw_log_payload)