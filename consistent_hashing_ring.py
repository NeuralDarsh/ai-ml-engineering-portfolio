# Distributed Systems & Caching: Minimizing key remapping during cluster scaling using consistent hash rings and virtual nodes

import hashlib
import bisect

class ConsistentHashRing:
    """
    Implements a Consistent Hashing ring with virtual nodes (vnodes)
    to distribute keys uniformly across a dynamic cluster of server nodes.
    """
    def __init__(self, replicas=3):
        self.replicas = replicas  # Virtual nodes per physical node
        self.ring = []            # Sorted list of virtual node hash keys
        self.ring_map = {}        # Hash key -> physical server ID
        self.nodes = set()

    def _hash(self, key):
        """Hashes string key to an integer position on the 32-bit integer ring."""
        digest = hashlib.md5(str(key).encode("utf-8")).hexdigest()
        return int(digest[:8], 16)

    def add_node(self, node_id):
        """Adds a physical node and places its virtual nodes onto the ring."""
        self.nodes.add(node_id)
        for i in range(self.replicas):
            vnode_key = f"{node_id}#vnode_{i}"
            vnode_hash = self._hash(vnode_key)
            self.ring_map[vnode_hash] = node_id
            bisect.insort(self.ring, vnode_hash)
        print(f" Added node '{node_id}' with {self.replicas} virtual nodes to hash ring.")

    def remove_node(self, node_id):
        """Removes a physical node and cleans up its virtual nodes from the ring."""
        if node_id not in self.nodes:
            return
        self.nodes.remove(node_id)
        for i in range(self.replicas):
            vnode_key = f"{node_id}#vnode_{i}"
            vnode_hash = self._hash(vnode_key)
            if vnode_hash in self.ring_map:
                del self.ring_map[vnode_hash]
                self.ring.remove(vnode_hash)
        print(f" Removed node '{node_id}' from hash ring.")

    def get_node(self, key):
        """
        Routes a data key to the first virtual node encountered clockwise on the ring.
        """
        if not self.ring:
            return None

        key_hash = self._hash(key)
        # Binary search for the first node with hash >= key_hash
        idx = bisect.bisect_right(self.ring, key_hash)
        
        # Wrap around to the start of the ring if at the end
        if idx == len(self.ring):
            idx = 0

        target_vnode_hash = self.ring[idx]
        assigned_node = self.ring_map[target_vnode_hash]
        return assigned_node

if __name__ == "__main__":
    print("--- Distributed Systems: Consistent Hashing Ring Simulator ---\n")

    # Initialize ring with 3 virtual nodes per server
    ch_ring = ConsistentHashRing(replicas=3)

    # 1. Add initial cluster servers
    ch_ring.add_node("cache-node-1")
    ch_ring.add_node("cache-node-2")
    ch_ring.add_node("cache-node-3")

    sample_keys = ["user:1001:profile", "order:994:details", "session:tok_abc", "cart:items:882", "auth:jwt:user4"]

    print("\nKey Routing on Initial 3-Node Cluster:")
    initial_allocations = {}
    for k in sample_keys:
        node = ch_ring.get_node(k)
        initial_allocations[k] = node
        print(f" Key '{k}' -> Routed to [{node}]")

    # 2. Scale cluster by adding a 4th node
    print("\nScaling Cluster: Adding 'cache-node-4'...")
    ch_ring.add_node("cache-node-4")

    print("\nKey Routing After Scaling:")
    remapped_count = 0
    for k in sample_keys:
        new_node = ch_ring.get_node(k)
        changed = "REMAPPED" if new_node != initial_allocations[k] else "STABLE"
        if new_node != initial_allocations[k]:
            remapped_count += 1
        print(f"Key '{k}' -> [{new_node}] ({changed})")

    print(f"\nSummary: Only {remapped_count}/{len(sample_keys)} keys migrated during scale-out.")