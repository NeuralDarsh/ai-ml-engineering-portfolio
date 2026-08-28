# Database Internals & Distributed Systems: Implementing sequential WAL append logs and state reconstruction after simulated crashes

import json
import time

class WriteAheadLogEngine:
    """
    Implements Write-Ahead Logging (WAL) and checkpoint-based recovery replay
    to guarantee atomicity and durability for in-memory key-value state.
    """
    def __init__(self):
        self.state = {}
        self.wal_log = []
        self.last_checkpoint_index = -1

    def append_log_and_apply(self, operation, key, value):
        """
        Appends mutation to WAL before applying state changes in memory.
        """
        log_entry = {
            "index": len(self.wal_log),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "operation": operation,  # "SET" or "DELETE"
            "key": key,
            "value": value
        }
        self.wal_log.append(log_entry)

        # Apply state transition
        if operation == "SET":
            self.state[key] = value
        elif operation == "DELETE" and key in self.state:
            del self.state[key]

        print(f" [WAL APPEND] Index: {log_entry['index']:<2} | Op: {operation:<6} | {key} = {value}")

    def create_checkpoint(self):
        """Saves active checkpoint marker to avoid full-log replaying."""
        self.last_checkpoint_index = len(self.wal_log) - 1
        print(f"\n [CHECKPOINT] Saved at WAL Index: {self.last_checkpoint_index}\n")

    def simulate_crash_and_recover(self):
        """
        Simulates ungraceful memory loss and recovers state by replaying WAL from last checkpoint.
        """
        print("\nSIMULATING CRASH: In-memory state cleared to empty...")
        self.state = {}  # Total memory wipe

        print("RECOVERY REPLAY: Scanning WAL from checkpoint onward...")
        replay_entries = self.wal_log[self.last_checkpoint_index + 1 :]

        for entry in replay_entries:
            op = entry["operation"]
            k = entry["key"]
            v = entry["value"]
            if op == "SET":
                self.state[k] = v
            elif op == "DELETE" and k in self.state:
                del self.state[k]
            print(f" [REPLAYED] Index {entry['index']}: {op} {k} -> {v}")

        print("\nRecovery Complete. Restored Database State:")
        print(json.dumps(self.state, indent=2))
        return self.state

if __name__ == "__main__":
    print("--- Database Systems: Write-Ahead Log (WAL) Recovery Engine ---\n")

    db = WriteAheadLogEngine()

    # 1. Standard mutations before checkpoint
    db.append_log_and_apply("SET", "user:101", {"name": "Darshan", "role": "ML Engineer"})
    db.append_log_and_apply("SET", "user:102", {"name": "Alex", "role": "DevOps"})
    db.create_checkpoint()

    # 2. Additional mutations executed after checkpoint
    db.append_log_and_apply("SET", "user:103", {"name": "Kenji", "role": "Architect"})
    db.append_log_and_apply("SET", "user:101", {"name": "Darshan", "role": "Senior AI Engineer"})
    db.append_log_and_apply("DELETE", "user:102", None)

    # 3. Simulate crash and trigger automatic replay recovery
    db.simulate_crash_and_recover()