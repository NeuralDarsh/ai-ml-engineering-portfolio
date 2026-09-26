# Distributed Transactions & Consensus: Implementing Coordinator-Cohort 2PC protocol with atomic commit and rollback recovery

import json
import uuid

class CohortParticipantNode:
    """
    Represents an independent shard or database participant in a distributed transaction.
    """
    def __init__(self, node_id, initial_balance=1000):
        self.node_id = node_id
        self.balance = initial_balance
        self.staged_transactions = {}  # tx_id -> delta

    def prepare(self, tx_id, delta):
        """
        Phase 1: Prepare
        Checks local invariants and stages mutation without committing.
        Returns True (VOTE_COMMIT) or False (VOTE_ABORT).
        """
        # Invariant check: balance cannot drop below zero
        if self.balance + delta < 0:
            print(f"[{self.node_id}] VOTE_ABORT: Insufficient balance ({self.balance} + {delta} < 0)")
            return False

        self.staged_transactions[tx_id] = delta
        print(f"[{self.node_id}] VOTE_COMMIT: Staged delta {delta} for Tx '{tx_id}'.")
        return True

    def commit(self, tx_id):
        """Phase 2: Global Commit - Applies staged mutation permanently."""
        if tx_id in self.staged_transactions:
            delta = self.staged_transactions.pop(tx_id)
            self.balance += delta
            print(f"[{self.node_id}] COMMITTED: New balance = {self.balance}")

    def abort(self, tx_id):
        """Phase 2: Global Abort - Discards staged mutation and rolls back."""
        if tx_id in self.staged_transactions:
            del self.staged_transactions[tx_id]
            print(f"[{self.node_id}] ROLLED BACK: Staged Tx '{tx_id}' purged.")


class TwoPhaseCommitCoordinator:
    """
    Coordinates distributed atomic transactions across multiple Cohort nodes.
    """
    def __init__(self, cohorts):
        self.cohorts = cohorts  # List of CohortParticipantNode

    def execute_transaction(self, operations):
        """
        Executes distributed atomic transfer across cohorts.
        operations: dict mapping node_id -> delta
        """
        tx_id = f"tx_2pc_{uuid.uuid4().hex[:6]}"
        print(f"\n--- Initiating Distributed Transaction: '{tx_id}' ---")
        print(f"Proposed operations: {operations}")

        # --- Phase 1: Prepare Phase ---
        print("\n[PHASE 1: PREPARE / VOTING]")
        votes = {}
        for node in self.cohorts:
            if node.node_id in operations:
                delta = operations[node.node_id]
                vote = node.prepare(tx_id, delta)
                votes[node.node_id] = vote

        # --- Phase 2: Decision Phase ---
        print("\n[PHASE 2: DECISION & EXECUTION]")
        all_approved = all(votes.values())

        if all_approved:
            print(f"Coordinator Decision: GLOBAL_COMMIT for Tx '{tx_id}'")
            for node in self.cohorts:
                if node.node_id in operations:
                    node.commit(tx_id)
            print("Distributed transaction successfully committed across all shards.\n")
            return True
        else:
            print(f" Coordinator Decision: GLOBAL_ABORT for Tx '{tx_id}' (At least one cohort aborted)")
            for node in self.cohorts:
                if node.node_id in operations:
                    node.abort(tx_id)
            print("Distributed transaction aborted and rolled back. No partial writes persisted.\n")
            return False


if __name__ == "__main__":
    print("--- Distributed Systems: Two-Phase Commit (2PC) Engine ---\n")

    # Initialize three participant shard nodes
    shard_alpha = CohortParticipantNode("shard_alpha", initial_balance=500)
    shard_beta = CohortParticipantNode("shard_beta", initial_balance=300)
    shard_gamma = CohortParticipantNode("shard_gamma", initial_balance=100)

    coordinator = TwoPhaseCommitCoordinator([shard_alpha, shard_beta, shard_gamma])

    # 1. Successful Distributed Transaction (Atomic transfer: alpha -> beta)
    print("Scenario 1: Valid Cross-Shard Balance Transfer:")
    coordinator.execute_transaction({
        "shard_alpha": -200,
        "shard_beta": 200
    })

    # 2. Failing Distributed Transaction (gamma fails balance invariant -> global abort)
    print("Scenario 2: Transfer where one shard violates constraint (Global Abort):")
    coordinator.execute_transaction({
        "shard_alpha": 100,
        "shard_gamma": -250  # gamma only has 100, will trigger VOTE_ABORT
    })

    # 3. Final State Audit
    print("Final Balances Across Shards:")
    balances = {node.node_id: node.balance for node in [shard_alpha, shard_beta, shard_gamma]}
    print(json.dumps(balances, indent=2))