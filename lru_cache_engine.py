# Backend Systems Engineering: Implementing an LRU caching policy with hit/miss tracking and capacity eviction

from collections import OrderedDict

class LRUCacheEngine:
    """
    Implements a Least Recently Used (LRU) cache of fixed capacity.
    Automatically moves accessed keys to the most-recent position
    and evicts the least-recently used key when capacity is exceeded.
    """
    def __init__(self, capacity=3):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.hits = 0
        self.misses = 0

    def get(self, key):
        """Retrieves a cached value and marks it as most recently used."""
        if key not in self.cache:
            self.misses += 1
            print(f" CACHE MISS: Key '{key}' not found.")
            return None

        # Mark as most recently used by moving it to the end
        self.cache.move_to_end(key)
        self.hits += 1
        print(f"CACHE HIT : Key '{key}' -> Value: {self.cache[key]}")
        return self.cache[key]

    def put(self, key, value):
        """Inserts or updates a value. Evicts the oldest item if capacity is exceeded."""
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value

        print(f" CACHE PUT : Key '{key}' = {value}")

        # Evict oldest entry (the first item) if over capacity
        if len(self.cache) > self.capacity:
            oldest_key, oldest_val = self.cache.popitem(last=False)
            print(f" EVICTION  : Capacity ({self.capacity}) exceeded. Evicted least recently used '{oldest_key}' = {oldest_val}")

    def get_telemetry(self):
        """Calculates cache efficiency metrics."""
        total_lookups = self.hits + self.misses
        hit_ratio = (self.hits / total_lookups * 100) if total_lookups > 0 else 0
        print("\nLRU Cache Telemetry Summary:")
        print(f"Total Hits   : {self.hits}")
        print(f"Total Misses : {self.misses}")
        print(f"Hit Ratio    : {hit_ratio:.1f}%")
        print(f"Active Keys  : {list(self.cache.keys())}\n")
        return {"hits": self.hits, "misses": self.misses, "hit_ratio_pct": round(hit_ratio, 1)}

if __name__ == "__main__":
    print("--- Systems Engineering: LRU Cache Eviction Simulator ---")
    print("Policy: Max Capacity = 3 entries\n")

    lru = LRUCacheEngine(capacity=3)

    # 1. Fill cache to capacity
    lru.put("user:101", {"name": "Darshan", "role": "Dev"})
    lru.put("user:102", {"name": "Alex", "role": "Analyst"})
    lru.put("user:103", {"name": "Sarah", "role": "Admin"})

    # 2. Access user:101 (making user:102 the least recently used)
    print("\nAccessing existing key to refresh LRU order:")
    lru.get("user:101")

    # 3. Add a fourth user to trigger eviction of user:102
    print("\nAdding new item to trigger eviction:")
    lru.put("user:104", {"name": "Kenji", "role": "Engineer"})

    # 4. Verify user:102 is gone and user:101 is still cached
    print("\nVerifying cache status:")
    lru.get("user:102")  # Expected Miss
    lru.get("user:101")  # Expected Hit

    lru.get_telemetry()