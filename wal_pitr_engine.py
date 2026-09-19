# Database Internals & Disaster Recovery: Implementing WAL segment rotation, base snapshots, and point-in-time state recovery

import time
import json
import uuid

class WALRecord:
    """Represents a discrete database mutation record in the WAL."""
    def __init__(self, tx_id, key, value, timestamp=None):
        self.tx_id = tx_id
        self.key = key
        self.value = value
        self.timestamp = timestamp or time.time()

    def to_dict(self):
        return {
            "tx_id": self.tx_id,
            "key": self.key,
            "value": self.value,
            "timestamp": self.timestamp
        }


class WALPITREngine:
    """
    Manages active WAL writes, immutable segment rotations,
    periodic base backups, and point-in-time recovery replaying.
    """
    def __init__(self, segment_capacity=3):
        self.segment_capacity = segment_capacity
        self.active_segment = []
        self.archived_segments = []
        self.base_backups = []  # List of {"snapshot": dict, "created_at": float}
        self.live_table = {}
        self.segment_counter = 0

    def write_mutation(self, key, value):
        """Atomically appends to WAL before applying to the active in-memory table."""
        tx_id = f"tx_{uuid.uuid4().hex[:6]}"
        record = WALRecord(tx_id, key, value)
        self.active_segment.append(record)
        self.live_table[key] = value

        print(f" [WAL LOG] Tx: {tx_id} | Key: '{key}' = '{value}' (Active Buffer: {len(self.active_segment)}/{self.segment_capacity})")

        if len(self.active_segment) >= self.segment_capacity:
            self._rotate_and_archive_segment()

    def _rotate_and_archive_segment(self):
        """Seals the active WAL segment and archives it to storage."""
        self.segment_counter += 1
        segment_id = f"wal_seg_{self.segment_counter:03d}.log"
        archived_entry = {
            "segment_id": segment_id,
            "records": [r.to_dict() for r in self.active_segment],
            "archived_at": time.time()
        }
        self.archived_segments.append(archived_entry)
        self.active_segment = []
        print(f"[WAL ARCHIVE] Sealed and rotated segment to '{segment_id}'.\n")

    def create_base_backup(self):
        """Creates a point-in-time full database snapshot."""
        snapshot = dict(self.live_table)
        backup_meta = {
            "snapshot": snapshot,
            "created_at": time.time()
        }
        self.base_backups.append(backup_meta)
        print(f"\n[BASE BACKUP] Captured full database snapshot: {snapshot}")
        return backup_meta["created_at"]

    def point_in_time_recovery(self, target_timestamp):
        """
        Restores the closest base backup prior to target_timestamp,
        then replays all subsequent WAL records up to target_timestamp.
        """
        print(f"\n--- Disaster Recovery: Running PITR up to timestamp {target_timestamp:.4f} ---")

        # 1. Locate the latest base backup created <= target_timestamp
        valid_backups = [b for b in self.base_backups if b["created_at"] <= target_timestamp]
        if not valid_backups:
            print(" Recovery Failed: No base backup found prior to the target time.")
            return None

        base_backup = max(valid_backups, key=lambda b: b["created_at"])
        restored_state = dict(base_backup["snapshot"])
        print(f"Restored base snapshot (from {base_backup['created_at']:.4f}): {restored_state}")

        # 2. Gather all WAL records from archives + active buffer
        all_records = []
        for seg in self.archived_segments:
            all_records.extend(seg["records"])
        all_records.extend([r.to_dict() for r in self.active_segment])

        # 3. Filter and sequentially replay records: base_backup_time < tx_time <= target_timestamp
        replay_count = 0
        for rec in all_records:
            if base_backup["created_at"] < rec["timestamp"] <= target_timestamp:
                restored_state[rec["key"]] = rec["value"]
                replay_count += 1
                print(f"[WAL REPLAY] Replayed Tx {rec['tx_id']}: '{rec['key']}' -> '{rec['value']}'")

        print(f"PITR Success: Replayed {replay_count} mutations. System recovered to target timestamp.")
        return restored_state


if __name__ == "__main__":
    print("--- Database Reliability: WAL Archival & PITR Simulator ---\n")

    engine = WALPITREngine(segment_capacity=2)

    # 1. Ingest initial mutations
    engine.write_mutation("service:auth", "v1.0.0")
    engine.write_mutation("service:gateway", "v1.2.0")  # Triggers segment rotation 1

    time.sleep(0.1)
    # 2. Capture a consistent base backup
    backup_time = engine.create_base_backup()
    time.sleep(0.1)

    # 3. Execute legitimate updates
    engine.write_mutation("service:payment", "v2.0.0")
    engine.write_mutation("service:auth", "v1.1.0")     # Triggers segment rotation 2
    time.sleep(0.1)

    # Save target timestamp right before accidental data corruption
    target_recovery_time = time.time()
    print(f"\n[CHECKPOINT] Target recovery timestamp recorded: {target_recovery_time:.4f}")
    time.sleep(0.1)

    # 4. Simulate catastrophic bad write / data corruption
    print("\nSimulating accidental table drop / corrupted write:")
    engine.write_mutation("service:payment", "CORRUPTED_NULL_VALUE")

    # 5. Execute PITR up to target_recovery_time
    recovered_db = engine.point_in_time_recovery(target_recovery_time)

    print("\nVerified Recovered Database State:")
    print(json.dumps(recovered_db, indent=2))