# Distributed Consensus & Fault Tolerance: Simulating Raft leader election, RequestVote RPCs, quorum counting, and AppendEntries heartbeats

import random
import json

class RaftNode:
    """
    Implements a single Raft consensus participant node supporting
    FOLLOWER, CANDIDATE, and LEADER state transitions.
    """
    FOLLOWER = "FOLLOWER"
    CANDIDATE = "CANDIDATE"
    LEADER = "LEADER"

    def __init__(self, node_id, cluster_nodes=None):
        self.node_id = node_id
        self.cluster_nodes = cluster_nodes or []
        self.current_term = 0
        self.voted_for = None
        self.state = self.FOLLOWER
        self.leader_id = None
        self.is_alive = True

    def start_election(self):
        """Transitions to CANDIDATE, increments term, votes for self, and requests votes."""
        if not self.is_alive:
            return

        self.state = self.CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id
        self.leader_id = None

        print(f"\n[{self.node_id}] Election Timeout triggered! Became CANDIDATE for Term {self.current_term}.")
        votes_received = 1  # Self vote

        # Broadcast RequestVote to peer nodes
        for peer in self.cluster_nodes:
            if peer.node_id != self.node_id and peer.is_alive:
                granted = peer.handle_request_vote(self.node_id, self.current_term)
                if granted:
                    votes_received += 1

        majority_threshold = (len([n for n in self.cluster_nodes if n.is_alive]) // 2) + 1
        print(f"[{self.node_id}] Received {votes_received} votes (Quorum threshold: {majority_threshold})")

        if votes_received >= majority_threshold:
            self.state = self.LEADER
            self.leader_id = self.node_id
            print(f"[{self.node_id}] ELECTED LEADER for Term {self.current_term}!")
            self.broadcast_heartbeats()
        else:
            self.state = self.FOLLOWER
            self.voted_for = None
            print(f"[{self.node_id}] Election failed. Reverted to FOLLOWER.")

    def handle_request_vote(self, candidate_id, term):
        """Evaluates inbound RequestVote RPC."""
        if not self.is_alive:
            return False

        # If incoming term is higher, step down and update term
        if term > self.current_term:
            self.current_term = term
            self.state = self.FOLLOWER
            self.voted_for = None
            self.leader_id = None

        if term == self.current_term and (self.voted_for is None or self.voted_for == candidate_id):
            self.voted_for = candidate_id
            print(f"[{self.node_id}] Voted FOR '{candidate_id}' in Term {term}")
            return True

        print(f"[{self.node_id}] Rejected vote for '{candidate_id}' (Already voted for: {self.voted_for})")
        return False

    def broadcast_heartbeats(self):
        """Leader broadcasts AppendEntries heartbeat to all followers."""
        if self.state != self.LEADER or not self.is_alive:
            return

        print(f"\n[{self.node_id}] Broadcasting AppendEntries Heartbeat (Term {self.current_term})...")
        for peer in self.cluster_nodes:
            if peer.node_id != self.node_id and peer.is_alive:
                peer.handle_append_entries(self.node_id, self.current_term)

    def handle_append_entries(self, leader_id, term):
        """Follower processes AppendEntries RPC, refreshing leadership."""
        if not self.is_alive:
            return False

        if term >= self.current_term:
            self.current_term = term
            self.state = self.FOLLOWER
            self.leader_id = leader_id
            self.voted_for = None
            print(f"[{self.node_id}] Heartbeat accepted from Leader '{leader_id}' (Term {term})")
            return True

        return False


if __name__ == "__main__":
    print("--- Distributed Consensus: Raft Minimal Protocol Engine ---\n")

    # 1. Initialize a 5-node Raft cluster
    node_ids = ["node_alpha", "node_beta", "node_gamma", "node_delta", "node_epsilon"]
    cluster = [RaftNode(nid) for nid in node_ids]

    # Link peers
    for node in cluster:
        node.cluster_nodes = cluster

    # 2. Trigger election on node_alpha
    print("Step 1: Initial Election Round on 'node_alpha':")
    cluster[0].start_election()

    # 3. Leader confirms authority via regular heartbeats
    print("\nStep 2: Leader Heartbeat Maintenance:")
    cluster[0].broadcast_heartbeats()

    # 4. Simulate sudden Leader crash
    print("\nStep 3: Leader 'node_alpha' crashes! (Simulating crash-stop failure)")
    cluster[0].is_alive = False

    # 5. Follower detects absence and initiates failover election
    print("\nStep 4: Failover Election initiated by 'node_beta':")
    cluster[1].start_election()

    # 6. Verify cluster state
    print("\nFinal Cluster Node State Summary:")
    summary = {
        n.node_id: {
            "state": n.state,
            "term": n.current_term,
            "leader": n.leader_id,
            "alive": n.is_alive
        }
        for n in cluster
    }
    print(json.dumps(summary, indent=2))