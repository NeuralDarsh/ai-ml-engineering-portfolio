# Database Internals & Storage Engines: High-throughput write pipelines with in-memory MemTables and immutable SSTables

import json
import time

class SSTableSegment:
    """
    Represents an immutable on-disk Sorted String Table (SSTable) file segment
    with an associated in-memory sparse primary key index for fast binary seeks.
    """
    def __init__(self, segment_id, sorted_entries):
        self.segment_id = segment_id
        self.data = sorted_entries  # Sorted list of (key, value) pairs
        self.sparse_index = {}      # Maps key -> offset position
        self._build_sparse_index(step=2)

    def _build_sparse_index(self, step=2):
        """Constructs a sparse index sampling keys every 'step' entries."""
        for idx in range(0, len(self.data), step):
            key = self.data[idx][0]
            self.sparse_index[key] = idx

    def get(self, key):
        """Performs a bounded linear scan using the sparse index."""
        # Check if key falls within range
        if not self.data or key < self.data[0][0] or key > self.data[-1][0]:
            return None

        # Determine scan start point via sparse index
        scan_start = 0
        for indexed_key, offset in sorted(self.sparse_index.items()):
            if indexed_key <= key:
                scan_start = offset
            else:
                break

        for idx in range(scan_start, len(self.data)):
            k, v = self.data[idx]
            if k == key:
                return v
            if k > key:
                break
        return None


class LSMTreeEngine:
    """
    Implements the core write path of an LSM-Tree.
    Buffers writes in a sorted MemTable and flushes to SSTables upon reaching capacity.
    """
    def __init__(self, memtable_capacity=4):
        self.memtable_capacity = memtable_capacity
        self.memtable = {}  # In-memory sorted buffer
        self.sstables = []  # Chronologically ordered SSTable segments (newest to oldest)
        self.segment_counter = 0

    def put(self, key, value):
        """Writes a key-value record to the active MemTable, flushing if threshold reached."""
        self.memtable[key] = value
        print(f" [MEMTABLE WRITE] Stored '{key}' = '{value}' (Size: {len(self.memtable)}/{self.memtable_capacity})")

        if len(self.memtable) >= self.memtable_capacity:
            self._flush_memtable()

    def _flush_memtable(self):
        """Sorts MemTable records and flushes them to an immutable SSTable segment."""
        self.segment_counter += 1
        segment_id = f"sstable_seg_{self.segment_counter:03d}"

        # Sort entries lexicographically by key
        sorted_entries = sorted(self.memtable.items(), key=lambda item: item[0])
        sstable = SSTableSegment(segment_id, sorted_entries)

        # Prepend so index 0 is always the newest segment
        self.sstables.insert(0, sstable)
        self.memtable.clear()

        print(f"\n[SSTABLE FLUSH] MemTable reached capacity! Flushed to immutable segment '{segment_id}'.")
        print(f" Segment Entries: {sorted_entries}")
        print(f" Sparse Index   : {sstable.sparse_index}\n")

    def get(self, key):
        """
        Reads a key by checking MemTable first, then traversing SSTables from newest to oldest.
        """
        print(f"--- LSM Read Query: Key = '{key}' ---")

        # 1. Search volatile MemTable
        if key in self.memtable:
            val = self.memtable[key]
            print(f" HIT in MemTable: '{key}' -> '{val}'\n")
            return val

        # 2. Search immutable SSTables sequentially
        for sstable in self.sstables:
            val = sstable.get(key)
            if val is not None:
                print(f" HIT in SSTable '{sstable.segment_id}': '{key}' -> '{val}'\n")
                return val

        print(f" MISS: Key '{key}' not found across any storage tier.\n")
        return None


if __name__ == "__main__":
    print("--- Storage Internals: LSM-Tree MemTable & SSTable Engine ---\n")

    lsm = LSMTreeEngine(memtable_capacity=3)

    # 1. Ingest records to trigger an SSTable flush
    print("Step 1: Ingesting batch 1 (Triggers Flush 1):")
    lsm.put("user_103", "Tokyo")
    lsm.put("user_101", "Kyoto")
    lsm.put("user_105", "Osaka")  # Hits capacity 3 -> flushes to sstable_seg_001

    # 2. Ingest batch 2
    print("Step 2: Ingesting batch 2 (Triggers Flush 2):")
    lsm.put("user_102", "Nagoya")
    lsm.put("user_104", "Fukuoka")
    lsm.put("user_106", "Sapporo")  # Hits capacity 3 -> flushes to sstable_seg_002

    # 3. Add record staying in active MemTable
    print("Step 3: Active MemTable write:")
    lsm.put("user_107", "Yokohama")

    # 4. Perform reads across storage hierarchy
    print("\nStep 4: Multi-tier point lookups:")
    lsm.get("user_107")  # Resolved from MemTable
    lsm.get("user_104")  # Resolved from SSTable Segment 2
    lsm.get("user_101")  # Resolved from SSTable Segment 1
    lsm.get("user_999")  # Non-existent key