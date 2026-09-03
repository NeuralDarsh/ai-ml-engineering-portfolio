# Distributed Storage & Messaging: Implementing Kafka-style key-based log compaction and tombstone retention

import json
import time

class LogCompactionEngine:
    """
    Simulates log compaction over an append-only event log.
    Retains the latest value per key and purges obsolete intermediate states and deleted tombstones.
    """
    def __init__(self):
        self.raw_log_segment = []

    def append_record(self, key, value):
        """Appends a new mutation or deletion tombstone (value=None) to the active log segment."""
        record = {
            "offset": len(self.raw_log_segment),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "key": key,
            "value": value  # None acts as a tombstone marker for deletion
        }
        self.raw_log_segment.append(record)
        action = "TOMBSTONE (DELETE)" if value is None else f"SET -> {value}"
        print(f" [LOG APPEND] Offset {record['offset']:<2} | Key: {key:<12} | {action}")

    def compact_log(self):
        """
        Executes compaction by scanning from oldest to newest offset.
        Retains only the latest offset per key, pruning tombstones once applied.
        """
        print("\n--- Distributed Storage: Running Log Compaction Routine ---")
        print(f"Original Segment Size: {len(self.raw_log_segment)} records\n")

        latest_key_records = {}

        # Scan log sequentially and retain only the most recent offset per key
        for record in self.raw_log_segment:
            latest_key_records[record["key"]] = record

        # Filter out tombstones (deleted items) in the final compacted segment
        compacted_segment = []
        for key, record in latest_key_records.items():
            if record["value"] is not None:
                compacted_segment.append(record)
            else:
                print(f" [PURGE TOMBSTONE] Key '{key}' explicitly removed from final segment.")

        # Sort compacted records by original offset order
        compacted_segment.sort(key=lambda r: r["offset"])

        reduction_pct = (1.0 - (len(compacted_segment) / len(self.raw_log_segment))) * 100 if self.raw_log_segment else 0.0

        print(f"\nCompaction Summary:")
        print(f" Initial Records    : {len(self.raw_log_segment)}")
        print(f" Compacted Records  : {len(compacted_segment)}")
        print(f" Storage Reduction  : {reduction_pct:.1f}%")
        print("\nFinal Compacted Segment:")
        print(json.dumps(compacted_segment, indent=2))

        self.raw_log_segment = compacted_segment
        return compacted_segment


if __name__ == "__main__":
    print("--- Messaging Architecture: Log Compaction Engine ---\n")

    engine = LogCompactionEngine()

    # 1. Simulate multiple updates to same keys across time
    engine.append_record("account:101", {"balance": 100.0, "status": "active"})
    engine.append_record("account:102", {"balance": 500.0, "status": "active"})
    engine.append_record("account:101", {"balance": 150.0, "status": "active"})  # Overwrites offset 0
    engine.append_record("account:103", {"balance": 300.0, "status": "active"})
    engine.append_record("account:102", {"balance": 450.0, "status": "active"})  # Overwrites offset 1
    engine.append_record("account:103", None)                                     # Tombstone: delete account:103
    engine.append_record("account:101", {"balance": 220.0, "status": "active"})  # Final update for 101

    # 2. Run compaction pass
    engine.compact_log()