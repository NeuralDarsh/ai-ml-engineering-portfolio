# Distributed Storage & Replication: Efficient background replica synchronization using hierarchical Merkle tree range reconciliation

import hashlib
import json

class MerkleRangeNode:
    """Represents a range-bounded node within a partitioned Merkle tree."""
    def __init__(self, range_start, range_end):
        self.range_start = range_start
        self.range_end = range_end
        self.hash_val = None
        self.left = None
        self.right = None
        self.items = {}  # Populated at leaf level: key -> value


class PartitionedMerkleTree:
    """
    Constructs a fixed-depth binary Merkle tree over partitioned key ranges
    to facilitate targeted anti-entropy reconciliation between replicas.
    """
    def __init__(self, num_buckets=4):
        self.num_buckets = num_buckets
        self.root = self._build_range_tree(0, num_buckets - 1)

    def _build_range_tree(self, start, end):
        node = MerkleRangeNode(start, end)
        if start == end:
            return node
        mid = (start + end) // 2
        node.left = self._build_range_tree(start, mid)
        node.right = self._build_range_tree(mid + 1, end)
        return node

    def _hash_str(self, text):
        return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]

    def populate(self, key_value_store):
        """Populates leaves based on hashed bucket assignment and computes internal hashes."""
        # Assign items to leaf buckets
        for k, v in key_value_store.items():
            bucket = int(hashlib.md5(k.encode("utf-8")).hexdigest(), 16) % self.num_buckets
            self._insert_leaf_item(self.root, bucket, k, v)

        # Bottom-up hash computation
        self._compute_hashes(self.root)

    def _insert_leaf_item(self, node, bucket, key, val):
        if node.left is None and node.right is None:
            node.items[key] = val
            return
        mid = (node.range_start + node.range_end) // 2
        if bucket <= mid:
            self._insert_leaf_item(node.left, bucket, key, val)
        else:
            self._insert_leaf_item(node.right, bucket, key, val)

    def _compute_hashes(self, node):
        if node.left is None and node.right is None:
            # Leaf node: hash sorted key-value pairs
            serialized = json.dumps(node.items, sort_keys=True)
            node.hash_val = self._hash_str(serialized)
            return node.hash_val

        left_h = self._compute_hashes(node.left)
        right_h = self._compute_hashes(node.right)
        node.hash_val = self._hash_str(f"{left_h}:{right_h}")
        return node.hash_val


class AntiEntropyCoordinator:
    """Compares replica Merkle trees to detect and reconcile out-of-sync buckets."""
    @classmethod
    def find_mismatched_buckets(cls, node_a, node_b):
        if node_a.hash_val == node_b.hash_val:
            return []  # Ranges are identical

        if node_a.left is None and node_a.right is None:
            # Leaf bucket mismatch found
            return [node_a.range_start]

        mismatches = []
        mismatches.extend(cls.find_mismatched_buckets(node_a.left, node_b.left))
        mismatches.extend(cls.find_mismatched_buckets(node_a.right, node_b.right))
        return mismatches

    @classmethod
    def reconcile(cls, store_primary, store_replica, num_buckets=4):
        print("--- Anti-Entropy: Generating Merkle Trees for Replicas ---")
        tree_a = PartitionedMerkleTree(num_buckets)
        tree_a.populate(store_primary)

        tree_b = PartitionedMerkleTree(num_buckets)
        tree_b.populate(store_replica)

        print(f"Primary Root Hash : {tree_a.root.hash_val}")
        print(f"Replica Root Hash : {tree_b.root.hash_val}\n")

        if tree_a.root.hash_val == tree_b.root.hash_val:
            print("Replicas are already synchronized. Zero network transfer required.\n")
            return

        mismatched_buckets = cls.find_mismatched_buckets(tree_a.root, tree_b.root)
        print(f"Divergence detected in Bucket(s): {mismatched_buckets}")

        # Selective repair: only copy keys falling in the divergent buckets
        synced_keys = []
        for k, v in store_primary.items():
            b = int(hashlib.md5(k.encode("utf-8")).hexdigest(), 16) % num_buckets
            if b in mismatched_buckets:
                if store_replica.get(k) != v:
                    store_replica[k] = v
                    synced_keys.append(k)

        print(f"Anti-Entropy Sync Complete! Reconciled keys: {synced_keys}\n")


if __name__ == "__main__":
    print("--- Distributed Storage: Anti-Entropy Merkle Reconciliation ---\n")

    primary_data = {
        "user:101": {"tier": "gold", "credits": 500},
        "user:102": {"tier": "silver", "credits": 120},
        "user:103": {"tier": "platinum", "credits": 950},
        "user:104": {"tier": "bronze", "credits": 40},
        "user:105": {"tier": "gold", "credits": 720}
    }

    replica_data = {
        "user:101": {"tier": "gold", "credits": 500},
        "user:102": {"tier": "silver", "credits": 50},  # Stale data
        "user:103": {"tier": "platinum", "credits": 950},
        "user:104": {"tier": "bronze", "credits": 40}
        # Missing user:105
    }

    # Run Anti-Entropy Reconciliation
    AntiEntropyCoordinator.reconcile(primary_data, replica_data, num_buckets=4)

    # Verify convergence
    print("Final Synchronized Replica Dataset:")
    print(json.dumps(replica_data, indent=2))