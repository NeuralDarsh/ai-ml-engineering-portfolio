# Database Storage & Performance: Amortizing fsync disk overhead via multi-transaction group batching

import threading
import time
import queue
import json

class TransactionCommitRequest:
    """Represents an individual client write transaction awaiting durable disk sync."""
    def __init__(self, tx_id, mutation):
        self.tx_id = tx_id
        self.mutation = mutation
        self.completed_event = threading.Event()
        self.assigned_lsn = None


class GroupCommitStorageEngine:
    """
    Simulates a high-throughput storage engine utilizing Group Commit.
    Batches concurrent write transactions into a single simulated fsync I/O operation.
    """
    def __init__(self, batch_window_ms=50, max_batch_size=8):
        self.batch_window = batch_window_ms / 1000.0
        self.max_batch_size = max_batch_size
        self.pending_queue = queue.Queue()
        self.running = True
        self.current_lsn = 1000  # Log Sequence Number
        self.persisted_log = []

        # Start background group commit worker thread
        self.worker_thread = threading.Thread(target=self._group_commit_loop, daemon=True)
        self.worker_thread.start()

    def commit(self, tx_id, mutation):
        """Client-facing API: Enqueues a transaction and blocks until the group commit flushes to disk."""
        req = TransactionCommitRequest(tx_id, mutation)
        self.pending_queue.put(req)

        # Block waiting for the group fsync to complete
        req.completed_event.wait()
        return req.assigned_lsn

    def _group_commit_loop(self):
        """Worker thread that assembles batches and triggers single durable writes."""
        while self.running:
            batch = []
            start_time = time.time()

            # 1. Collect pending transactions within the time window or until batch cap
            while (time.time() - start_time) < self.batch_window and len(batch) < self.max_batch_size:
                try:
                    remaining_timeout = max(0.001, self.batch_window - (time.time() - start_time))
                    req = self.pending_queue.get(timeout=remaining_timeout)
                    batch.append(req)
                except queue.Empty:
                    break

            if not batch:
                continue

            # 2. Execute single consolidated disk I/O (Simulated fsync)
            self._execute_batch_fsync(batch)

    def _execute_batch_fsync(self, batch):
        batch_ids = [r.tx_id for r in batch]
        print(f"\n--- Group Commit Triggered: Batch Size = {len(batch)} ---")
        print(f" Transactions in Group: {batch_ids}")

        # Simulate expensive disk fsync latency (e.g. 30ms physical drive sync)
        time.sleep(0.03)

        self.current_lsn += len(batch)
        synced_at = time.time()

        for idx, req in enumerate(batch):
            req.assigned_lsn = self.current_lsn - len(batch) + idx + 1
            self.persisted_log.append({
                "lsn": req.assigned_lsn,
                "tx_id": req.tx_id,
                "mutation": req.mutation
            })
            # 3. Notify waiting thread that its data is durably stored
            req.completed_event.set()

        print(f"[FSYNC PERSISTED] Flushed {len(batch)} transactions in single I/O. Base LSN: {self.current_lsn}\n")

    def shutdown(self):
        self.running = False
        self.worker_thread.join(timeout=1.0)


if __name__ == "__main__":
    print("--- Storage Internals: Group Commit & Batch Flusher ---\n")

    engine = GroupCommitStorageEngine(batch_window_ms=60, max_batch_size=5)

    def client_worker(worker_id, key, val):
        tx_id = f"tx_worker_{worker_id}"
        print(f"Client [{tx_id}] submitting mutation '{key}'='{val}'...")
        lsn = engine.commit(tx_id, {key: val})
        print(f"Client [{tx_id}] committed durably at LSN #{lsn}!")

    # Spawn 6 concurrent client threads to trigger group batching
    threads = []
    sample_mutations = [
        ("wallet:101", 1500),
        ("wallet:102", 3400),
        ("wallet:103", 850),
        ("wallet:104", 4200),
        ("wallet:105", 990),
        ("wallet:106", 2100)
    ]

    for i, (k, v) in enumerate(sample_mutations, start=1):
        t = threading.Thread(target=client_worker, args=(i, k, v))
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    engine.shutdown()

    print("\nFinal Durable WAL Log Entries:")
    print(json.dumps(engine.persisted_log, indent=2))