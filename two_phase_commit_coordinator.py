# Distributed Systems & Databases: Coordinating atomic multi-service transactions with Prepare and Commit/Rollback phases

import time

class ParticipantNode:
    """
    Represents an independent microservice node participating in a 2PC transaction.
    """
    def __init__(self, name, should_succeed=True):
        self.name = name
        self.should_succeed = should_succeed
        self.prepared_state = None
        self.committed_state = None

    def prepare(self, tx_id, data):
        """Phase 1: Validates and locks resource. Returns vote boolean."""
        if not self.should_succeed:
            print(f" [{self.name}] Vote: VOTE_ABORT (Resource conflict / validation failed)")
            return False
        self.prepared_state = data
        print(f"[{self.name}] Vote: VOTE_COMMIT (Resource successfully reserved)")
        return True

    def commit(self, tx_id):
        """Phase 2a: Applies the prepared mutation permanently."""
        self.committed_state = self.prepared_state
        self.prepared_state = None
        print(f" [{self.name}] Applied GLOBAL_COMMIT for Tx '{tx_id}'.")

    def rollback(self, tx_id):
        """Phase 2b: Reverts prepared mutation and unlocks resource."""
        self.prepared_state = None
        print(f" [{self.name}] Applied GLOBAL_ROLLBACK for Tx '{tx_id}'.")


class TwoPhaseCommitCoordinator:
    """
    Coordinates distributed atomic transactions across registered participant nodes.
    """
    def __init__(self, participants):
        self.participants = participants

    def execute_transaction(self, tx_id, payload):
        print(f"--- Distributed Systems: 2PC Coordinator [Tx: {tx_id}] ---")
        print("Phase 1: PREPARE (Voting Phase)")

        votes = {}
        all_ready = True

        # Phase 1: Solicit votes from all participants
        for node in self.participants:
            vote = node.prepare(tx_id, payload)
            votes[node.name] = vote
            if not vote:
                all_ready = False

        print("\nPhase 2: DECISION & EXECUTION")
        if all_ready:
            print(" ALL NODES READY -> Broadcasting GLOBAL_COMMIT:")
            for node in self.participants:
                node.commit(tx_id)
            verdict = "COMMITTED"
        else:
            print(" ONE OR MORE NODES ABORTED -> Broadcasting GLOBAL_ROLLBACK:")
            for node in self.participants:
                node.rollback(tx_id)
            verdict = "ABORTED"

        print(f"\nTransaction Summary: Status = {verdict}\n")
        return verdict


if __name__ == "__main__":
    # Test Case 1: Successful Distributed Transaction (All nodes healthy)
    nodes_healthy = [
        ParticipantNode("PaymentService", should_succeed=True),
        ParticipantNode("InventoryService", should_succeed=True),
        ParticipantNode("NotificationService", should_succeed=True)
    ]
    coordinator_1 = TwoPhaseCommitCoordinator(nodes_healthy)
    coordinator_1.execute_transaction("tx_1001", {"order_id": "ord_881", "amount": 450.00})

    print("=" * 60 + "\n")

    # Test Case 2: Failed Distributed Transaction (Inventory node fails)
    nodes_flaky = [
        ParticipantNode("PaymentService", should_succeed=True),
        ParticipantNode("InventoryService", should_succeed=False),  # Out of stock / failure
        ParticipantNode("NotificationService", should_succeed=True)
    ]
    coordinator_2 = TwoPhaseCommitCoordinator(nodes_flaky)
    coordinator_2.execute_transaction("tx_1002", {"order_id": "ord_882", "amount": 120.00})