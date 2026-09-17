# Distributed Streaming & Messaging: Implementing consumer group partition rebalancing and deterministic range assignment

import json

class ConsumerInstance:
    """Represents an active consumer node within a consumer group."""
    def __init__(self, member_id):
        self.member_id = member_id
        self.assigned_partitions = []

    def assign_partitions(self, partitions):
        self.assigned_partitions = partitions
        print(f"[{self.member_id}] Claimed partitions: {self.assigned_partitions}")

    def revoke_partitions(self):
        revoked = self.assigned_partitions
        self.assigned_partitions = []
        if revoked:
            print(f"[{self.member_id}] Revoked partitions: {revoked}")
        return revoked


class ConsumerGroupCoordinator:
    """
    Coordinates partition assignments across a consumer group.
    Triggers rebalancing routines whenever members join or leave.
    """
    def __init__(self, topic_name, total_partitions):
        self.topic_name = topic_name
        self.total_partitions = total_partitions
        self.members = {}  # member_id -> ConsumerInstance

    def register_consumer(self, member_id):
        """Adds a consumer to the group and triggers a rebalance pass."""
        print(f"--- Consumer Group: Member '{member_id}' Joined ---")
        consumer = ConsumerInstance(member_id)
        self.members[member_id] = consumer
        self.rebalance()
        return consumer

    def deregister_consumer(self, member_id):
        """Removes a consumer (failure/shutdown) and reassigns partitions."""
        print(f"--- Consumer Group: Member '{member_id}' Left/Failed ---")
        if member_id in self.members:
            self.members[member_id].revoke_partitions()
            del self.members[member_id]
            self.rebalance()

    def rebalance(self):
        """
        Executes a deterministic Range Assignment strategy:
        Divides partitions into contiguous ranges across sorted member IDs.
        """
        active_member_ids = sorted(self.members.keys())
        num_members = len(active_member_ids)

        print("\n[REBALANCE TRIGGERED] Reassigning topic partitions across active members...")

        if num_members == 0:
            print(" No active consumers available. All partitions unassigned.\n")
            return

        # Revoke all active leases first to ensure clean state transitions
        for member in self.members.values():
            member.revoke_partitions()

        partitions_per_member = self.total_partitions // num_members
        extra_partitions = self.total_partitions % num_members

        start_partition = 0
        for i, member_id in enumerate(active_member_ids):
            # Distribute remainder partitions to the first few consumers
            count = partitions_per_member + (1 if i < extra_partitions else 0)
            end_partition = start_partition + count
            assigned = list(range(start_partition, end_partition))
            self.members[member_id].assign_partitions(assigned)
            start_partition = end_partition

        print("[REBALANCE COMPLETE] Group state stabilized.\n")

    def get_assignment_map(self):
        return {
            m_id: c.assigned_partitions
            for m_id, c in self.members.items()
        }


if __name__ == "__main__":
    print("--- Messaging Infrastructure: Partition Consumer Rebalancer ---\n")

    # Topic with 8 partitions (0 to 7)
    coordinator = ConsumerGroupCoordinator(topic_name="telemetry_events", total_partitions=8)

    # 1. First consumer joins (Claims all 8 partitions)
    c1 = coordinator.register_consumer("consumer-instance-A")

    # 2. Second consumer joins (Triggers rebalance: 4 partitions each)
    c2 = coordinator.register_consumer("consumer-instance-B")

    # 3. Third consumer joins (Triggers rebalance: 3, 3, and 2 partitions)
    c3 = coordinator.register_consumer("consumer-instance-C")

    # 4. Simulate consumer crash/leave
    coordinator.deregister_consumer("consumer-instance-B")

    # 5. Final assignment audit
    print("Final Partition Allocation State:")
    print(json.dumps(coordinator.get_assignment_map(), indent=2))