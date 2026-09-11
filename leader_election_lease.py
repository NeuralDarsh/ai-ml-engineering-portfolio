# Distributed Systems & Consensus: Dynamic leader coordination, lease timeouts, and automated failover election

import time

class CentralLeaseCoordinator:
    """
    Simulates a centralized coordination service (like etcd or ZooKeeper)
    that manages a single active leader lease with a time-to-live (TTL).
    """
    def __init__(self, lease_ttl=2.0):
        self.lease_ttl = lease_ttl
        self.current_leader = None
        self.lease_expires_at = 0.0
        self.term = 0

    def try_acquire_or_renew_lease(self, candidate_node_id):
        now = time.time()

        # 1. Lease renewal by the active leader
        if self.current_leader == candidate_node_id and now < self.lease_expires_at:
            self.lease_expires_at = now + self.lease_ttl
            print(f"[HEARTBEAT] Leader '{candidate_node_id}' renewed lease (Term {self.term}) until {self.lease_expires_at:.2f}")
            return True

        # 2. Lease expired or unassigned: Elect new leader
        if now >= self.lease_expires_at:
            old_leader = self.current_leader
            self.current_leader = candidate_node_id
            self.lease_expires_at = now + self.lease_ttl
            self.term += 1
            print(f" [NEW LEADER ELECTED] Node '{candidate_node_id}' acquired lease for Term {self.term} (Previous: {old_leader})")
            return True

        # 3. Active lease held by another node
        return False


class ClusterNode:
    """Represents a node participating in cluster leadership and failover."""
    def __init__(self, node_id, coordinator):
        self.node_id = node_id
        self.coordinator = coordinator
        self.is_leader = False
        self.is_alive = True

    def step(self):
        """Attempts to renew lease if leader, or run election if follower."""
        if not self.is_alive:
            return

        acquired = self.coordinator.try_acquire_or_renew_lease(self.node_id)
        if acquired and not self.is_leader:
            self.is_leader = True
            print(f" [{self.node_id}] Transitioned to LEADER state.")
        elif not acquired and self.is_leader:
            self.is_leader = False
            print(f"  [{self.node_id}] Stepped down to FOLLOWER state.")


if __name__ == "__main__":
    print("--- Distributed Systems: Leader Election & Lease Simulator ---\n")

    coordinator = CentralLeaseCoordinator(lease_ttl=1.5)

    node_1 = ClusterNode("node_alpha", coordinator)
    node_2 = ClusterNode("node_beta", coordinator)
    node_3 = ClusterNode("node_gamma", coordinator)

    cluster = [node_1, node_2, node_3]

    # 1. Initial election round: node_alpha claims leadership
    print("Step 1: Initial Election Race:")
    for node in cluster:
        node.step()

    # 2. Leader sends periodic heartbeats to maintain lease
    print("\nStep 2: Leader Maintains Lease via Heartbeats:")
    for _ in range(2):
        time.sleep(0.4)
        node_1.step()

    # 3. Simulate sudden leader crash (node_alpha dies)
    print("\nStep 3: Simulating crash of 'node_alpha' (Heartbeats stop)...")
    node_1.is_alive = False

    # Wait past lease TTL threshold
    print("Sleeping 1.8s past lease expiration window...\n")
    time.sleep(1.8)

    # 4. Failover election: Remaining nodes race to claim vacant lease
    print("Step 4: Cluster Failover Detection & Re-election:")
    node_2.step()
    node_3.step()

    print(f"\nFinal Coordinator State: Active Leader = '{coordinator.current_leader}' (Term {coordinator.term})")