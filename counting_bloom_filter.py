# Distributed Systems & Storage: Space-efficient probabilistic set membership supporting dynamic item removal

import hashlib
import math

class CountingBloomFilter:
    """
    Implements an in-memory Counting Bloom Filter.
    Supports constant-time insertions, queries, and deletions using counter buckets.
    """
    def __init__(self, size=50, num_hashes=3):
        self.size = size
        self.num_hashes = num_hashes
        self.buckets = [0] * size
        self.item_count = 0

    def _get_hashes(self, item):
        """Generates deterministic bucket indices across hash iterations."""
        indices = []
        raw_str = str(item)
        for seed in range(self.num_hashes):
            digest = hashlib.md5(f"{seed}:{raw_str}".encode("utf-8")).hexdigest()
            index = int(digest[:8], 16) % self.size
            indices.append(index)
        return indices

    def add(self, item):
        """Inserts an element by incrementing counter buckets."""
        indices = self._get_hashes(item)
        for idx in indices:
            self.buckets[idx] += 1
        self.item_count += 1
        print(f" [ADDED] Item: '{item}' -> Buckets incremented: {indices}")

    def contains(self, item):
        """Checks potential set membership. Returns False (definitely not in set) or True (likely in set)."""
        indices = self._get_hashes(item)
        match = all(self.buckets[idx] > 0 for idx in indices)
        status = "PROBABLE MATCH" if match else "DEFINITELY NOT IN SET"
        print(f"[QUERY] Item: '{item}' -> {status}")
        return match

    def remove(self, item):
        """Safely removes an item by decrementing counters with underflow protection."""
        if not self.contains(item):
            print(f"[DELETE ABORTED] Item: '{item}' not found in filter.")
            return False

        indices = self._get_hashes(item)
        for idx in indices:
            if self.buckets[idx] > 0:
                self.buckets[idx] -= 1

        self.item_count = max(0, self.item_count - 1)
        print(f" [DELETED] Item: '{item}' -> Buckets decremented: {indices}")
        return True

    def calculate_false_positive_rate(self):
        """Calculates theoretical false positive probability: (1 - e^(-kn/m))^k."""
        if self.item_count == 0:
            return 0.0
        k = self.num_hashes
        m = self.size
        n = self.item_count
        prob = (1.0 - math.exp(-1.0 * (k * n) / m)) ** k
        return prob


if __name__ == "__main__":
    print("--- Storage & Datastores: Counting Bloom Filter ---\n")

    cbf = CountingBloomFilter(size=30, num_hashes=3)

    # 1. Insert items
    print("Step 1: Adding items to filter:")
    cbf.add("user_session_101")
    cbf.add("user_session_102")
    cbf.add("blocked_ip_192.168.1.50")

    print("\nStep 2: Querying membership:")
    cbf.contains("user_session_101")
    cbf.contains("unregistered_user_999")

    # 2. Estimate current false positive rate
    fpr = cbf.calculate_false_positive_rate()
    print(f"\nEstimated False Positive Probability: {fpr * 100:.3f}%\n")

    # 3. Dynamic deletion of an item
    print("Step 3: Removing an item:")
    cbf.remove("user_session_101")

    print("\nStep 4: Re-querying removed item:")
    cbf.contains("user_session_101")