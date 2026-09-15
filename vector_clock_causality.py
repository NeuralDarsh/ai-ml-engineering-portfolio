# Distributed Systems & Consensus: Capturing partial event ordering and detecting concurrent state conflicts

import json

class VectorClock:
    """
    Implements a logical Vector Clock to track causal ordering across distributed nodes.
    Supports local increments, message synchronization, and partial order comparisons.
    """
    def __init__(self, node_id):
        self.node_id = node_id
        self.clock = {node_id: 0}

    def tick(self):
        """Increments the local node's logical timestamp."""
        self.clock[self.node_id] = self.clock.get(self.node_id, 0) + 1
        return dict(self.clock)

    def merge(self, incoming_clock):
        """
        Merges an incoming remote vector clock into local state
        by taking the element-wise maximum for each node counter.
        """
        all_nodes = set(self.clock.keys()).union(incoming_clock.keys())
        for node in all_nodes:
            self.clock[node] = max(self.clock.get(node, 0), incoming_clock.get(node, 0))
        # Tick local clock to mark the merge event
        self.tick()

    @staticmethod
    def compare(v1, v2):
        """
        Compares two vector clocks to determine their causal relationship:
        Returns 'BEFORE', 'AFTER', 'EQUAL', or 'CONCURRENT'.
        """
        all_nodes = set(v1.keys()).union(v2.keys())
        v1_greater = False
        v2_greater = False

        for node in all_nodes:
            c1 = v1.get(node, 0)
            c2 = v2.get(node, 0)
            if c1 > c2:
                v1_greater = True
            elif c2 > c1:
                v2_greater = True

        if v1_greater and not v2_greater:
            return "AFTER"       # v1 happened after v2 (v2 causally preceded v1)
        elif v2_greater and not v1_greater:
            return "BEFORE"      # v1 happened before v2
        elif not v1_greater and not v2_greater:
            return "EQUAL"
        else:
            return "CONCURRENT"  # Simultaneous edits / split-brain conflict


class DistributedNode:
    """Represents an independent node maintaining local state with vector clocks."""
    def __init__(self, node_id):
        self.node_id = node_id
        self.vc = VectorClock(node_id)
        self.data_store = {}

    def mutate_state(self, key, value):
        """Executes a local state change and increments the vector clock."""
        clock_snapshot = self.vc.tick()
        self.data_store[key] = {"val": value, "clock": clock_snapshot}
        print(f" {self.node_id}] Set '{key}' = '{value}' | Vector: {clock_snapshot}")

    def sync_with_peer(self, peer_node, key):
        """Simulates bidirectional synchronization and detects concurrent conflicts."""
        print(f"\nSyncing '{self.node_id}' with '{peer_node.node_id}' for key '{key}':")
        local_entry = self.data_store.get(key)
        peer_entry = peer_node.data_store.get(key)

        if not local_entry or not peer_entry:
            return

        relation = VectorClock.compare(local_entry["clock"], peer_entry["clock"])
        print(f" Causal Relation: Local is [{relation}] Peer")

        if relation == "CONCURRENT":
            print(f" CONFLICT DETECTED: Concurrent uncoordinated writes on key '{key}'!")
            print(f"-> {self.node_id} Clock: {local_entry['clock']}")
            print(f"-> {peer_node.node_id} Clock: {peer_entry['clock']}")
        elif relation == "BEFORE":
            print(f" Updating {self.node_id} with newer state from {peer_node.node_id}.")
            self.data_store[key] = peer_entry
        else:
            print(f" {self.node_id} already holds latest or equal state.")

        # Reconcile clocks
        self.vc.merge(peer_entry["clock"])
        peer_node.vc.merge(local_entry["clock"])


if __name__ == "__main__":
    print("--- Distributed Systems: Vector Clock Causality Engine ---\n")

    node_a = DistributedNode("Node-A")
    node_b = DistributedNode("Node-B")

    # 1. Node-A performs a mutation
    print("Step 1: Sequential mutation on Node-A:")
    node_a.mutate_state("doc_title", "Portfolio Architecture")

    # 2. Node-A sends state to Node-B (Causal precedence)
    node_b.data_store["doc_title"] = node_a.data_store["doc_title"]
    node_b.vc.merge(node_a.data_store["doc_title"]["clock"])

    # 3. Simulate network partition: Both nodes perform independent concurrent updates
    print("\nStep 2: Concurrent mutations during network partition:")
    node_a.mutate_state("doc_title", "Distributed Systems Handbook")
    node_b.mutate_state("doc_title", "Applied AI & Systems Guide")

    # 4. Attempt to sync post-partition (Triggers CONCURRENT detection)
    node_a.sync_with_peer(node_b, "doc_title")