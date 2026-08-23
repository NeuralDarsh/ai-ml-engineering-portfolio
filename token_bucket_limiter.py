# API Gateways & Traffic Management: Controlling request burst capacity and steady-state throughput using token buckets

import time

class TokenBucketLimiter:
    """
    Implements the Token Bucket algorithm to regulate API request rates.
    Supports burst capacities and continuous fractional token replenishment over time.
    """
    def __init__(self, capacity=5, refill_rate_per_sec=1.0):
        self.capacity = float(capacity)
        self.refill_rate = float(refill_rate_per_sec)
        self.tokens = float(capacity)
        self.last_refill = time.time()

    def _replenish(self):
        """Calculates token accumulation based on time elapsed since the last request."""
        now = time.time()
        elapsed = now - self.last_refill
        
        # Add newly accumulated tokens based on elapsed duration
        self.tokens = min(self.capacity, self.tokens + (elapsed * self.refill_rate))
        self.last_refill = now

    def consume(self, tokens_needed=1):
        """
        Attempts to consume the required tokens for an inbound request.
        Returns True if allowed, False if throttled.
        """
        self._replenish()
        
        print(f"--- Gateway Traffic Shaper: Token Bucket Audit ---")
        print(f"  Requested Tokens : {tokens_needed}")
        print(f"  Available Tokens : {self.tokens:.2f} / {self.capacity:.1f}")

        if self.tokens >= tokens_needed:
            self.tokens -= tokens_needed
            print(f"  [ALLOWED] Tokens remaining: {self.tokens:.2f}\n")
            return True
        else:
            deficit = tokens_needed - self.tokens
            wait_time = deficit / self.refill_rate
            print(f"  [THROTTLED] Bucket depleted! (HTTP 429 | Refill wait: ~{wait_time:.2f}s)\n")
            return False

if __name__ == "__main__":
    # Configure a bucket: max burst capacity = 3 tokens, regenerates 1 token per second
    limiter = TokenBucketLimiter(capacity=3, refill_rate_per_sec=1.0)

    # 1. Simulate an instant burst of 4 single-token requests
    print(" Test 1: Rapid burst of 4 requests:")
    for i in range(1, 5):
        print(f"Request #{i}:")
        limiter.consume(1)
        time.sleep(0.2)

    # 2. Wait for tokens to replenish
    print("Sleeping for 2.2 seconds to regenerate tokens...\n")
    time.sleep(2.2)

    # 3. Retry after regeneration
    print("Test 2: Inbound request after replenishment:")
    limiter.consume(1)