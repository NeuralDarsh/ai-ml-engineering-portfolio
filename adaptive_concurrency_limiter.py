# Systems Reliability & Cloud Gateways: Dynamic in-flight request bounding using TCP-style latency feedback

import time
import random

class LoadShedException(Exception):
    """Raised when in-flight capacity is exhausted and incoming calls are dropped."""
    pass


class AdaptiveConcurrencyLimiter:
    """
    Dynamically adjusts concurrent in-flight request limits based on observed RTT latency.
    Employs Additive Increase / Multiplicative Decrease (AIMD) to avoid overload collapses.
    """
    def __init__(self, min_limit=2, max_limit=30, backoff_factor=0.7, tolerance_ratio=1.5):
        self.min_limit = min_limit
        self.max_limit = max_limit
        self.backoff_factor = backoff_factor
        self.tolerance_ratio = tolerance_ratio

        self.concurrency_limit = float(min_limit + 4)
        self.in_flight = 0
        self.rtt_min = None  # Baseline minimum observed RTT (ms)

    def acquire(self):
        """Attempts to register an in-flight request. Drops request if limit exceeded."""
        if self.in_flight >= int(self.concurrency_limit):
            print(f"[LOAD SHED] In-flight ({self.in_flight}) reached limit ({int(self.concurrency_limit)}). Fast failing.")
            raise LoadShedException("Service overloaded: Request shed by adaptive limiter.")
        
        self.in_flight += 1
        return True

    def release(self, latency_ms):
        """Releases the in-flight slot and updates the adaptive concurrency limit via AIMD."""
        self.in_flight = max(0, self.in_flight - 1)

        # Initialize or update minimum baseline RTT
        if self.rtt_min is None or latency_ms < self.rtt_min:
            self.rtt_min = latency_ms

        rtt_threshold = self.rtt_min * self.tolerance_ratio

        if latency_ms <= rtt_threshold:
            # Additive Increase: Network/CPU is healthy, expand capacity
            old_limit = self.concurrency_limit
            self.concurrency_limit = min(self.max_limit, self.concurrency_limit + 1.0)
            print(f"[LATENCY HEALTHY] RTT: {latency_ms:.1f}ms <= {rtt_threshold:.1f}ms | Limit: {old_limit:.1f} -> {self.concurrency_limit:.1f}")
        else:
            # Multiplicative Decrease: Latency spike detected, throttle concurrency
            old_limit = self.concurrency_limit
            self.concurrency_limit = max(float(self.min_limit), self.concurrency_limit * self.backoff_factor)
            print(f" [CONGESTION DETECTED] RTT: {latency_ms:.1f}ms > {rtt_threshold:.1f}ms | Throttle: {old_limit:.1f} -> {self.concurrency_limit:.1f}")


if __name__ == "__main__":
    print("--- Systems Resilience: Adaptive Concurrency Limiter ---\n")

    limiter = AdaptiveConcurrencyLimiter(min_limit=2, max_limit=15)

    def handle_request(req_id, simulated_latency_ms):
        print(f"--- Inbound Request #{req_id} ---")
        try:
            limiter.acquire()
            # Simulate work
            time.sleep(simulated_latency_ms / 1000.0)
            limiter.release(simulated_latency_ms)
        except LoadShedException as err:
            print(f"Dropped: {err}")

    # Phase 1: Baseline operations with stable low latency (~20ms)
    print("Phase 1: Healthy low-latency requests (Additive Increase):")
    for i in range(1, 4):
        handle_request(i, simulated_latency_ms=20.0)

    # Phase 2: Downstream database slowdown occurs (Latency spikes to 90ms)
    print("\nPhase 2: Latency spike due to backend saturation (Multiplicative Decrease):")
    for i in range(4, 7):
        handle_request(i, simulated_latency_ms=95.0)

    # Phase 3: High concurrency arrives while limit is compressed (Demonstrates load shedding)
    print("\nPhase 3: Simulating concurrent flood on constrained limiter:")
    active_tokens = 0
    for req in range(1, 8):
        try:
            limiter.acquire()
            active_tokens += 1
            print(f"Admitted token {req} (In-flight: {limiter.in_flight})")
        except LoadShedException:
            pass

    # Clean up tokens
    for _ in range(active_tokens):
        limiter.release(25.0)

    print(f"\nFinal Stabilized Concurrency Limit: {limiter.concurrency_limit:.1f}")