# Distributed Systems & Consensus: Multi-master conflict-free synchronization using Observed-Removed Sets (OR-Set)

import uuid
import json

class ORSetReplica:
    """
    Implements a state-based Observed-Removed Set (OR-Set) CRDT.
    Guarantees strong eventual consistency across replicas without coordination.
    """
    def __init__(self, replica_id):
        self.replica_id = replica_id
        # add_set stores tuples: (element, unique_tag)
        self.add_set = set()
        # remove_set stores observed tags: unique_tag
        self.remove_set = set()

    def add(self, element):
        """Adds an element by tagging it with a globally unique identifier."""
        tag = f"{self.replica_id}_{uuid.uuid4().hex[:6]}"
        self.add_set.add((element, tag))
        print(f"[{self.replica_id}] ADD: '{element}' (Tag: {tag})")
        return tag

    def remove(self, element):
        """
        Removes an element by adding all currently observed tags for that element
        to the tombstone remove_set.
        """
        observed_tags = {tag for (elem, tag) in self.add_set if elem == element}
        if not observed_tags:
            print(f"[{self.replica_id}] REMOVE IGNORED: '{element}' not found in observed state.")
            return

        self.remove_set.update(observed_tags)
        print(f"[{self.replica_id}] REMOVE: '{element}' (Observed tags purged: {observed_tags})")

    def read(self):
        """
        Computes the effective active set:
        Elements with at least one tag in add_set that has NOT been added to remove_set.
        """
        active_elements = {
            elem for (elem, tag) in self.add_set
            if tag not in self.remove_set
        }
        return sorted(list(active_elements))

    def merge(self, remote_replica):
        """
        Merges state from another replica via set union:
        AddSet_new = AddSet_local ∪ AddSet_remote
        RemoveSet_new = RemoveSet_local ∪ RemoveSet_remote
        """
        print(f"\n[CRDT MERGE] Syncing replica '{self.replica_id}' with '{remote_replica.replica_id}'...")
        self.add_set.update(remote_replica.add_set)
        self.remove_set.update(remote_replica.remove_set)
        print(f"Convergence reached. Active elements: {self.read()}")


if __name__ == "__main__":
    print("--- Distributed Consensus: CRDT OR-Set Sync Engine ---\n")

    # 1. Initialize two isolated replicas (e.g. Tokyo & Mumbai edge nodes)
    replica_tokyo = ORSetReplica("Node-Tokyo")
    replica_mumbai = ORSetReplica("Node-Mumbai")

    # 2. Both nodes add shared elements independently
    print("Step 1: Initial local mutations:")
    replica_tokyo.add("item:laptop")
    replica_tokyo.add("item:display")

    replica_mumbai.add("item:keyboard")

    # 3. Synchronize initial state
    replica_tokyo.merge(replica_mumbai)
    replica_mumbai.merge(replica_tokyo)

    # 4. Simulate network partition: Concurrent edits
    print("\nStep 2: Concurrent mutations during network partition:")
    # Tokyo removes "item:display"
    replica_tokyo.remove("item:display")

    # Mumbai concurrently re-adds "item:display" (new tag) and adds "item:mouse"
    replica_mumbai.add("item:display")
    replica_mumbai.add("item:mouse")

    print(f"\nTokyo State pre-sync  : {replica_tokyo.read()}")
    print(f"Mumbai State pre-sync : {replica_mumbai.read()}")

    # 5. Network partition heals: Bidirectional CRDT merge
    print("\nStep 3: Network partition heals - merging states:")
    replica_tokyo.merge(replica_mumbai)
    replica_mumbai.merge(replica_tokyo)

    # 6. Verify identical convergence (Notice 'item:display' survives because Mumbai added a newer unobserved tag)
    print("\nFinal Converged States:")
    print(f"Tokyo Final  : {json.dumps(replica_tokyo.read())}")
    print(f"Mumbai Final : {json.dumps(replica_mumbai.read())}")
    assert replica_tokyo.read() == replica_mumbai.read(), "CRDT Convergence validation failed!"
    print(" Strong Eventual Consistency verified without conflict markers!")