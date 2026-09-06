# Distributed Storage & Cryptography: Hierarchical hash trees for efficient data consistency checks and tamper localization

import hashlib
import json

class MerkleTreeNode:
    """Represents a node within the Merkle Tree."""
    def __init__(self, hash_value, left=None, right=None, data_chunk=None):
        self.hash_value = hash_value
        self.left = left
        self.right = right
        self.data_chunk = data_chunk


class MerkleTreeEngine:
    """
    Constructs a binary Merkle Tree from data blocks and provides
    fast root-level consistency verification and tamper localization.
    """
    @staticmethod
    def _sha256(data_str):
        return hashlib.sha256(data_str.encode("utf-8")).hexdigest()

    def build_tree(self, data_blocks):
        """Constructs a Merkle Tree from an ordered list of string chunks."""
        if not data_blocks:
            return None

        # 1. Create leaf nodes
        current_level = [
            MerkleTreeNode(self._sha256(str(chunk)), data_chunk=str(chunk))
            for chunk in data_blocks
        ]

        # 2. Iteratively pair nodes and compute parent hashes until single root remains
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left_child = current_level[i]
                
                # If odd number of nodes, duplicate the last node
                if i + 1 < len(current_level):
                    right_child = current_level[i + 1]
                else:
                    right_child = MerkleTreeNode(left_child.hash_value, data_chunk=left_child.data_chunk)

                parent_hash = self._sha256(left_child.hash_value + right_child.hash_value)
                parent_node = MerkleTreeNode(parent_hash, left=left_child, right=right_child)
                next_level.append(parent_node)

            current_level = next_level

        return current_level[0]

    def get_root_hash(self, root_node):
        return root_node.hash_value if root_node else None

    def find_tampered_chunks(self, original_node, replica_node):
        """
        Recursively traverses both trees to isolate exactly which leaf blocks do not match.
        """
        if not original_node or not replica_node:
            return []

        # If hashes match, entire subtree is identical
        if original_node.hash_value == replica_node.hash_value:
            return []

        # If leaf reached and mismatch detected
        if original_node.left is None and replica_node.left is None:
            return [{
                "expected": original_node.data_chunk,
                "found": replica_node.data_chunk,
                "expected_hash": original_node.hash_value[:10] + "...",
                "replica_hash": replica_node.hash_value[:10] + "..."
            }]

        discrepancies = []
        discrepancies.extend(self.find_tampered_chunks(original_node.left, replica_node.left))
        discrepancies.extend(self.find_tampered_chunks(original_node.right, replica_node.right))
        return discrepancies


if __name__ == "__main__":
    print("--- Distributed Storage: Merkle Tree Integrity Engine ---\n")

    engine = MerkleTreeEngine()

    original_dataset = [
        "account:101:bal=500",
        "account:102:bal=1250",
        "account:103:bal=80",
        "account:104:bal=9300"
    ]

    replica_dataset = [
        "account:101:bal=500",
        "account:102:bal=9999",  # Tampered / desynchronized record
        "account:103:bal=80",
        "account:104:bal=9300"
    ]

    tree_primary = engine.build_tree(original_dataset)
    tree_replica = engine.build_tree(replica_dataset)

    root_primary = engine.get_root_hash(tree_primary)
    root_replica = engine.get_root_hash(tree_replica)

    print(f"Primary Merkle Root : {root_primary}")
    print(f"Replica Merkle Root : {root_replica}\n")

    if root_primary == root_replica:
        print("Datasets are identical across replicas.")
    else:
        print("Merkle Root mismatch detected! Pinpointing corrupted chunks...")
        corrupted = engine.find_tampered_chunks(tree_primary, tree_replica)
        print(json.dumps(corrupted, indent=2))