# Distributed Systems & Networking: Decentralized cluster state synchronization and failure detection using epidemic gossip

import random
import time
import json

class GossipNode:
    """
    Represents an independent node participating in a decentralized gossip cluster.
    Tracks local heartbeat counters and a synchronized membership table.
    """
    def __init__(self, node_id, fail_timeout=4.0):
        self.node_id = node_id
        self.fail_timeout = fail_timeout
        self.heartbeat = 0
        # Membership table maps: node_id -> {"heartbeat": int, "last_updated": float, "status": "ALIVE"|"DEAD"}
        self.membership_table = {
            self.node_id: {"heartbeat": 0, "last_updated": time.time(), "status": "ALIVE"}
        }
        self.is_running = True

    def increment_heartbeat(self):
        """Ticks the local node's heartbeat forward."""
        if not self.is_running:
            return
        self.heartbeat += 1
        self.membership_table[self.node_id] = {
            "heartbeat": self.heartbeat,
            "last_updated": time.time(),
            "status": "ALIVE"
        }

    def prepare_gossip_digest(self):
        """Exports membership state for gossip exchange."""
        return self.membership_table

    def merge_gossip_digest(self, peer_table):
        """Merges another node's gossip table into local state using highest heartbeat."""
        now = time.time()
        for peer_id, info in peer_table.items():
            current = self.membership_table.get(peer_id)
            if not current or info["heartbeat"] > current["heartbeat"]:
                self.membership_table[peer_id] = {
                    "heartbeat": info["heartbeat"],
                    "last_updated": now,
                    "status": "ALIVE"
                }

    def audit_failures(self):
        """Scans membership table to mark unupdated peers as DEAD."""
        now = time.time()
        for peer_id, info in self.membership_table.items():
            if peer_id != self.node_id and info["status"] == "ALIVE":
                if (now - info["last_updated"]) > self.fail_timeout:
                    info["status"] = "DEAD"
                    print(f" [{self.node_id}] DETECTED FAILURE: Peer '{peer_id}' timed out -> Marked DEAD.")


class GossipClusterSimulator:
    """Orchestrates gossip rounds across an ensemble of distributed nodes."""
    def __init__(self, nodes):
        self.nodes = {n.node_id: n for n in nodes}

    def execute_gossip_round(self):
        # 1. Increment local heartbeats
        for node in self.nodes.values():
            node.increment_heartbeat()

        # 2. Pick a random peer for each running node and exchange state
        active_nodes = [n for n in self.nodes.values() if n.is_running]
        for node in active_nodes:
            peers = [p for p in active_nodes if p.node_id != node.node_id]
            if peers:
                target = random.choice(peers)
                # Bi-directional gossip sync
                target.merge_gossip_digest(node.prepare_gossip_digest())
                node.merge_gossip_digest(target.prepare_gossip_digest())

        # 3. Detect node timeouts
        for node in active_nodes:
            node.audit_failures()


if __name__ == "__main__":
    print("--- Distributed Systems: Gossip Protocol Failure Detector ---\n")

    cluster_nodes = [
        GossipNode("node_alpha", fail_timeout=1.5),
        GossipNode("node_beta", fail_timeout=1.5),
        GossipNode("node_gamma", fail_timeout=1.5),
        GossipNode("node_delta", fail_timeout=1.5)
    ]
    simulator = GossipClusterSimulator(cluster_nodes)

    # Initial rounds of healthy gossipopp
    print("Simulating 3 normal gossip synchronization rounds:")
    for r in range(1, 4):
        print(f"--- Round {r} ---")
        simulator.execute_gossip_round()
        time.sleep(0.3)

    # Simulate node_gamma crashing
    print("\nSimulating sudden crash of 'node_gamma'...")
    cluster_nodes[2].is_running = False

    # Wait past timeout window
    print("Sleeping 1.8 seconds past fail timeout threshold...\n")
    time.sleep(1.8)

    print("Executing gossip round post-crash:")
    simulator.execute_gossip_round()

    print("\nFinal Cluster State Observed by 'node_alpha':")
    print(json.dumps(cluster_nodes[0].membership_table, indent=2))