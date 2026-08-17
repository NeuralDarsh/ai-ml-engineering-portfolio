# Distributed Systems Engineering: Implementing a 3-state circuit breaker to prevent cascading system failures

import time

class CircuitBreakerEngine:
    """
    Implements a Circuit Breaker pattern with CLOSED, OPEN, and HALF-OPEN states.
    Fails fast when downstream error thresholds are reached to protect system stability.
    """
    def __init__(self, failure_threshold=3, recovery_timeout=4.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = "CLOSED"  # CLOSED, OPEN, HALF-OPEN
        self.failure_count = 0
        self.last_state_change = time.time()

    def call(self, func, *args, **kwargs):
        current_time = time.time()

        # Check if OPEN breaker is ready to transition to HALF-OPEN
        if self.state == "OPEN":
            if current_time - self.last_state_change > self.recovery_timeout:
                self.state = "HALF-OPEN"
                self.last_state_change = current_time
                print(f" CIRCUIT HALF-OPEN: Recovery timeout elapsed. Testing downstream service...")
            else:
                remaining = round(self.recovery_timeout - (current_time - self.last_state_change), 2)
                print(f"CIRCUIT OPEN: Call blocked immediately! (Fail Fast | Cooldown remaining: {remaining}s)")
                return None

        # Execute target function
        try:
            result = func(*args, **kwargs)
            self._handle_success()
            return result
        except Exception as err:
            self._handle_failure(err)
            return None

    def _handle_success(self):
        if self.state in ["HALF-OPEN", "OPEN"]:
            print("CIRCUIT CLOSED: Downstream service recovered successfully.")
        self.state = "CLOSED"
        self.failure_count = 0

    def _handle_failure(self, error):
        self.failure_count += 1
        print(f" EXECUTION FAILURE ({self.failure_count}/{self.failure_threshold}): {error}")

        if self.failure_count >= self.failure_threshold or self.state == "HALF-OPEN":
            self.state = "OPEN"
            self.last_state_change = time.time()
            print(f" CIRCUIT TRIPPED TO OPEN: Threshold reached. Blocking subsequent calls.")

if __name__ == "__main__":
    print("--- Systems Engineering: Circuit Breaker Simulator ---")
    print("Policy: Failure Threshold = 3, Recovery Timeout = 3.0s\n")

    breaker = CircuitBreakerEngine(failure_threshold=3, recovery_timeout=3.0)

    # Simulated unstable external API endpoint
    def flaky_external_service(attempt):
        if attempt < 4:
            raise ConnectionError("500 Internal Server Error: Database Unreachable")
        return "200 OK: Data processed successfully"

    # 1. Trigger consecutive failures to trip the circuit
    print("Triggering consecutive failures:")
    for i in range(1, 4):
        print(f"Attempt #{i}:")
        breaker.call(flaky_external_service, i)

    # 2. Attempt call while circuit is OPEN (fails fast)
    print("\nAttempting call while OPEN:")
    breaker.call(flaky_external_service, 4)

    # 3. Wait for recovery timeout to transition to HALF-OPEN
    print("\nSleeping 3.2 seconds for breaker recovery timeout...\n")
    time.sleep(3.2)

    # 4. Probe call in HALF-OPEN state (recovers circuit)
    print("Executing probe call:")
    breaker.call(flaky_external_service, 4)