# Distributed Systems & Resilience: Preventing cascading microservice outages via finite state machine circuit tripping

import time

class CircuitBreakerOpenException(Exception):
    """Raised when an operation is rejected by an OPEN circuit breaker."""
    pass


class CircuitBreakerSentinel:
    """
    Implements the Circuit Breaker pattern with CLOSED, OPEN, and HALF_OPEN states.
    Monitors execution error rates and permits trial canary probes after a cooldown period.
    """
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

    def __init__(self, failure_threshold=3, recovery_timeout=2.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = self.CLOSED
        self.consecutive_failures = 0
        self.last_state_change = time.time()

    def _check_state_transition(self):
        """Transitions from OPEN to HALF_OPEN once the cooldown timeout elapses."""
        if self.state == self.OPEN:
            elapsed = time.time() - self.last_state_change
            if elapsed >= self.recovery_timeout:
                self.state = self.HALF_OPEN
                self.last_state_change = time.time()
                print(f"\n[COOLDOWN ELAPSED] Circuit transitioned: OPEN -> HALF_OPEN (Canary trial active)")

    def call(self, operation_callable, *args, **kwargs):
        """Executes operation under circuit breaker surveillance."""
        self._check_state_transition()

        print(f"--- Resilience Sentinel: Inbound Call [State: {self.state}] ---")

        if self.state == self.OPEN:
            print("[SHORT-CIRCUITED] Call rejected immediately (Fast Fallback triggered).")
            raise CircuitBreakerOpenException("Circuit is OPEN. Fast fail active.")

        try:
            result = operation_callable(*args, **kwargs)
            self._on_success()
            return result
        except Exception as err:
            self._on_failure(err)
            raise err

    def _on_success(self):
        """Handles successful execution and resets state if in HALF_OPEN."""
        if self.state == self.HALF_OPEN:
            print("[CANARY SUCCESS] Downstream service recovered. Transitioning: HALF_OPEN -> CLOSED.")
            self.state = self.CLOSED
            self.last_state_change = time.time()
        self.consecutive_failures = 0
        print("[EXECUTION OK] Request processed successfully.\n")

    def _on_failure(self, err):
        """Tracks consecutive failures and trips breaker to OPEN when threshold is met."""
        self.consecutive_failures += 1
        print(f"[EXECUTION FAILED] Error: {err} (Failures: {self.consecutive_failures}/{self.failure_threshold})")

        if self.state in [self.CLOSED, self.HALF_OPEN] and self.consecutive_failures >= self.failure_threshold:
            self.state = self.OPEN
            self.last_state_change = time.time()
            print(f"[BREAKER TRIPPED] Threshold exceeded! Transitioning -> OPEN.\n")


if __name__ == "__main__":
    print("--- Systems Resilience: Circuit Breaker Sentinel ---\n")

    breaker = CircuitBreakerSentinel(failure_threshold=2, recovery_timeout=1.5)

    is_downstream_healthy = False

    def simulated_api_call():
        if not is_downstream_healthy:
            raise ConnectionError("Downstream Payment Service 503 Unavailable")
        return {"status": "SUCCESS", "transaction_id": "tx_88921"}

    # 1. Trigger consecutive failures until circuit trips to OPEN
    print("Test 1: Simulating failing downstream service:")
    for i in range(1, 4):
        try:
            breaker.call(simulated_api_call)
        except Exception:
            pass

    # 2. Attempt call while circuit is OPEN (Should fail immediately without querying service)
    print("Test 2: Attempting call while OPEN (Fast Failure):")
    try:
        breaker.call(simulated_api_call)
    except CircuitBreakerOpenException:
        pass

    # 3. Wait for cooldown to expire
    print("\nSleeping 1.6s for cooldown recovery timeout...\n")
    time.sleep(1.6)

    # 4. Restore downstream health and execute canary probe in HALF-OPEN
    print("Test 3: Downstream recovers; running canary test in HALF-OPEN:")
    is_downstream_healthy = True
    breaker.call(simulated_api_call)

    # 5. Normal operation resumed
    breaker.call(simulated_api_call)