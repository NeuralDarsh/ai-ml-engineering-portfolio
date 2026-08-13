# Security & Network Engineering: Auditing API response headers, enforcing security policies, and injecting standard headers

import json

def enforce_http_header_policy(raw_headers):
    """
    Audits a dictionary of HTTP response headers, injects mandatory security policies
    (X-Content-Type-Options, X-Frame-Options, Strict-Transport-Security),
    and redacts revealing server identification tokens.
    """
    print("--- Security Engineering: HTTP Response Header Policy Injector ---")
    
    # 1. Normalize headers dictionary keys to lower-case for case-insensitive lookup
    normalized_headers = {k.lower(): v for k, v in raw_headers.items()}
    
    # Mandatory production security header definitions
    required_security_headers = {
        "x-content-type-options": "nosniff",
        "x-frame-options": "DENY",
        "strict-transport-security": "max-age=31536000; includeSubDomains",
        "x-xss-protection": "1; mode=block",
        "content-type": "application/json; charset=utf-8"
    }
    
    injected_count = 0
    modified_headers = dict(raw_headers)
    
    # 2. Inject missing security policies
    for header_key, default_value in required_security_headers.items():
        if header_key not in normalized_headers:
            # Preserve standard Header-Case formatting for final output
            formatted_key = "-".join([word.capitalize() for word in header_key.split("-")])
            modified_headers[formatted_key] = default_value
            injected_count += 1
            print(f"  Injected Missing Policy: {formatted_key} = '{default_value}'")
            
    # 3. Redact revealing server metadata tokens to prevent information disclosure
    sensitive_keys = ["server", "x-powered-by"]
    for key in list(modified_headers.keys()):
        if key.lower() in sensitive_keys:
            print(f" Redacted Information Disclosure Header: {key}")
            del modified_headers[key]
            
    print("\nHeader Policy Enforcement Report:")
    print(f"  Total Policies Injected : {injected_count}")
    print("  Final Enforced Response Headers:")
    print(json.dumps(modified_headers, indent=4))
    print("\n  POLICY VERDICT: Response headers conform to security standards.")
    
    return modified_headers

if __name__ == "__main__":
    # Simulated weak HTTP response headers from an unconfigured microservice
    sample_weak_response_headers = {
        "Content-Type": "application/json",
        "Server": "Apache/2.4.41 (Ubuntu)",
        "X-Powered-By": "Express",
        "Cache-Control": "no-cache"
    }
    
    enforce_http_header_policy(sample_weak_response_headers)