# Cloud Infrastructure & Networking: Progressive weighted traffic splitting, telemetry rollback, and graceful connection draining

import random
import time
import json

class ServiceCluster:
    """Represents a deployed backend version cluster (Stable or Canary)."""
    def __init__(self, name, version, error_rate=0.0):
        self.name = name
        self.version = version
        self.error_rate = error_rate  # Simulated synthetic failure probability
        self.active_connections = 0
        self.total_requests = 0
        self.draining = False

    def handle_request(self, req_id):
        if self.draining:
            raise RuntimeError(f"Cluster '{self.name}' is DRAINING. Rejecting new connections.")

        self.active_connections += 1
        self.total_requests += 1

        # Simulate brief execution
        time.sleep(0.01)
        is_error = random.random() < self.error_rate

        self.active_connections = max(0, self.active_connections - 1)

        if is_error:
            raise ConnectionError(f"500 Internal Error from {self.name} ({self.version})")

        return f"200 OK from {self.name} [{self.version}]"


class CanaryTrafficShifter:
    """
    Coordinates progressive traffic shifting between Stable and Canary clusters.
    Enforces error-threshold rollbacks and orchestrates graceful connection draining.
    """
    def __init__(self, stable_cluster, canary_cluster, canary_weight=0.0):
        self.stable = stable_cluster
        self.canary = canary_cluster
        self.canary_weight = canary_weight  # Float between 0.0 (0%) and 1.0 (100%)
        self.consecutive_canary_errors = 0
        self.rollback_triggered = False

    def set_weights(self, canary_weight):
        """Adjusts the runtime routing ratio."""
        self.canary_weight = max(0.0, min(1.0, canary_weight))
        print(f"[WEIGHT SHIFT] Canary Weight set to {self.canary_weight * 100:.0f}% (Stable: {(1.0 - self.canary_weight) * 100:.0f}%)")

    def route_request(self, req_id):
        """Routes inbound request based on current split weights and health telemetry."""
        if self.rollback_triggered:
            target = self.stable
        else:
            # Weighted random selection
            target = self.canary if random.random() < self.canary_weight else self.stable

        try:
            res = target.handle_request(req_id)
            if target == self.canary:
                self.consecutive_canary_errors = 0
            print(f"[REQ #{req_id:03d}] -> {res}")
            return res
        except Exception as err:
            print(f"[REQ #{req_id:03d}] -> Failed on {target.name}: {err}")
            if target == self.canary:
                self.consecutive_canary_errors += 1
                if self.consecutive_canary_errors >= 2:
                    self._trigger_rollback()
            return None

    def _trigger_rollback(self):
        """Automatically resets canary weight to 0 upon persistent errors."""
        print(f"\n[AUTOMATED ROLLBACK] Canary error threshold exceeded! Clamping canary traffic to 0%.")
        self.canary_weight = 0.0
        self.rollback_triggered = True

    def drain_and_retire(self, cluster, timeout_sec=2.0):
        """Initiates graceful connection draining before de-registration."""
        print(f"\n[DRAINING INITIATED] Marking '{cluster.name}' as DRAINING...")
        cluster.draining = True
        start = time.time()

        while cluster.active_connections > 0 and (time.time() - start) < timeout_sec:
            print(f"  Waiting for {cluster.active_connections} active connections to finish...")
            time.sleep(0.05)

        print(f"[DRAIN COMPLETE] Cluster '{cluster.name}' safely de-registered with 0 lost connections.\n")


if __name__ == "__main__":
    print("--- Cloud Gateways: Dynamic Canary Traffic Shifter & Drain Simulator ---\n")

    cluster_stable = ServiceCluster("Cluster-Stable", "v1.4.0", error_rate=0.0)
    cluster_canary = ServiceCluster("Cluster-Canary", "v1.5.0-rc1", error_rate=0.0)

    proxy = CanaryTrafficShifter(cluster_stable, cluster_canary, canary_weight=0.10)

    # Phase 1: Initial 10% Canary Probe
    print("Phase 1: Routing initial 10% canary traffic:")
    for i in range(1, 11):
        proxy.route_request(i)

    # Phase 2: Scale up canary to 50%
    print("\nPhase 2: Scaling canary traffic to 50%:")
    proxy.set_weights(0.50)
    for i in range(11, 21):
        proxy.route_request(i)

    # Phase 3: Simulate bug injected into canary -> triggers automated rollback
    print("\nPhase 3: Canary encounters regression (Simulating 100% failure rate):")
    cluster_canary.error_rate = 1.0
    for i in range(21, 25):
        proxy.route_request(i)

    # Phase 4: Gracefully drain failed canary cluster
    proxy.drain_and_retire(cluster_canary)

    # Telemetry report
    print("Final Execution Stats:")
    print(json.dumps({
        "stable_requests": cluster_stable.total_requests,
        "canary_requests": cluster_canary.total_requests,
        "rollback_executed": proxy.rollback_triggered
    }, indent=2))