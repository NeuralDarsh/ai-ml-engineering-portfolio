# Developer Tooling: Extracting rate limit quota headers and calculating reset time deltas

import time
from datetime import datetime

def parse_rate_limit_headers(headers):
    """
    Parses HTTP response headers for rate limit quotas and computes 
    the remaining requests and cooldown duration before reset.
    """
    print("--- Developer Tools: API Rate Limit Header Parser ---")
    
    # 1. Normalize header keys to lower-case for case-insensitive lookup
    normalized_headers = {k.lower(): v for k, v in headers.items()}
    
    limit = int(normalized_headers.get("x-ratelimit-limit", 60))
    remaining = int(normalized_headers.get("x-ratelimit-remaining", 0))
    reset_epoch = int(normalized_headers.get("x-ratelimit-reset", time.time() + 60))
    
    current_time = int(time.time())
    cooldown_seconds = max(0, reset_epoch - current_time)
    reset_time_str = datetime.fromtimestamp(reset_epoch).strftime("%H:%M:%S")
    
    print("API Quota Status Report:")
    print(f"Total Allowed Limit : {limit} requests")
    print(f"Remaining Capacity  : {remaining} requests")
    print(f"Reset Timestamp     : {reset_time_str} (Unix Epoch: {reset_epoch})")
    print(f"Cooldown Countdown  : {cooldown_seconds} seconds remaining\n")
    
    # 2. Defensive Request Routing Decision Matrix
    if remaining == 0:
        print(f"QUOTA EXHAUSTED: Pause outgoing requests for {cooldown_seconds} seconds.")
        return {"allow_request": False, "wait_seconds": cooldown_seconds}
    elif remaining < (limit * 0.1): # Less than 10% remaining
        print("WARNING: Low rate limit remaining. Throttle request speed.")
        return {"allow_request": True, "wait_seconds": 2.0}
    else:
        print("SAFE: Ample quota available. Proceed with API request.")
        return {"allow_request": True, "wait_seconds": 0.0}

if __name__ == "__main__":
    # Simulated HTTP response headers from an API gateway
    mock_headers_exhausted = {
        "X-RateLimit-Limit": "5000",
        "X-RateLimit-Remaining": "0",
        "X-RateLimit-Reset": str(int(time.time()) + 45), # Resets in 45 seconds
        "Content-Type": "application/json"
    }
    
    verdict = parse_rate_limit_headers(mock_headers_exhausted)
    print(f"\nExecution Verdict: {verdict}")