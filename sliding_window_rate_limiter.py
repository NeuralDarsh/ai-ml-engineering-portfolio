# Backend & API Gateway Engineering: Enforcing API request thresholds using sliding window timestamp logs

import time
from collections import deque

class SlidingWindowRateLimiter:
    """
    Implements a sliding window rate limiter that tracks access timestamps
    per client ID and rejects requests exceeding the configured threshold.
    """
    def __init__(self, max_requests=5, window_seconds=10.0):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Maps client_id -> deque of access timestamps
        self.client_request_logs = {}

    def allow_request(self, client_id):
        current_time = time.time()
        
        if client_id not in self.client_request_logs:
            self.client_request_logs[client_id] = deque()
            
        timestamp_queue = self.client_request_logs[client_id]
        
        # 1. Evict timestamps that fall outside the current sliding time window
        threshold_time = current_time - self.window_seconds
        while timestamp_queue and timestamp_queue[0] <= threshold_time:
            timestamp_queue.popleft()
            
        # 2. Check if remaining requests are within the allowed quota
        if len(timestamp_queue) < self.max_requests:
            timestamp_queue.append(current_time)
            remaining_quota = self.max_requests - len(timestamp_queue)
            print(f"[ALLOWED] Client '{client_id}' | Remaining Window Quota: {remaining_quota}/{self.max_requests}")
            return True
        else:
            oldest_entry = timestamp_queue[0]
            retry_after = round(self.window_seconds - (current_time - oldest_entry), 2)
            print(f"[BLOCKED] Client '{client_id}' Rate Limit Exceeded! (429 Too Many Requests | Retry After: {retry_after}s)")
            return False

if __name__ == "__main__":
    print("--- Backend Systems: Sliding Window Rate Limiter Simulator ---")
    print("Policy: Max 3 requests per 5.0-second sliding window\n")
    
    limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=5.0)
    target_client = "user_darshan_dev"
    
    # Simulate a burst of 5 rapid requests from the same user
    print("Simulating rapid client request burst...")
    for i in range(1, 6):
        print(f"Request #{i}:")
        limiter.allow_request(target_client)
        time.sleep(0.5)
        
    # Simulate waiting for the window to slide and refresh quota
    print("\n Sleeping for 3.5 seconds to let sliding window expire oldest requests...\n")
    time.sleep(3.5)
    
    print("Retrying request after window cool-down:")
    limiter.allow_request(target_client)