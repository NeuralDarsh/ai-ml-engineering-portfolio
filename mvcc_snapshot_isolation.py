# Database Internals & Concurrency: Implementing non-blocking snapshot reads and write-write conflict detection

import time
import json

class RowVersion:
    """Represents an immutable version of a database record."""
    def __init__(self, key, value, created_tx_id):
        self.key = key
        self.value = value
        self.created_tx_id = created_tx_id
        self.expired_tx_id = None  # Populated when updated or deleted


class MVCCStorageEngine:
    """
    Manages multi-version record storage and evaluates visibility rules
    based on transaction snapshot isolation boundaries.
    """
    def __init__(self):
        self._tx_counter = 0
        # key -> list of RowVersion instances (oldest to newest)
        self._table = {}
        self._active_transactions = set()

    def begin_transaction(self):
        """Starts a new transaction, capturing an active snapshot ID."""
        self._tx_counter += 1
        tx_id = self._tx_counter
        self._active_transactions.add(tx_id)
        print(f" [BEGIN TX] Started Transaction Tx-{tx_id} (Snapshot ID: {tx_id})")
        return tx_id

    def read(self, tx_id, key):
        """
        Reads the latest record version visible to this transaction's snapshot.
        Rules: created_tx_id <= tx_id AND (expired_tx_id is None OR expired_tx_id > tx_id).
        """
        versions = self._table.get(key, [])
        for version in reversed(versions):
            # Must have been created before or at this snapshot
            if version.created_tx_id <= tx_id:
                # Must not have been deleted/superseded before this snapshot
                if version.expired_tx_id is None or version.expired_tx_id > tx_id:
                    print(f" [READ] Tx-{tx_id} read '{key}' = '{version.value}' (v-created by Tx-{version.created_tx_id})")
                    return version.value

        print(f"[READ] Tx-{tx_id} found no visible version for key '{key}'")
        return None

    def write(self, tx_id, key, value):
        """
        Creates a new version of a key. Validates write-write conflicts.
        """
        if key not in self._table:
            self._table[key] = []

        versions = self._table[key]
        active_version = None
        for v in reversed(versions):
            if v.expired_tx_id is None:
                active_version = v
                break

        # Write-Write Conflict Detection: Cannot overwrite if updated by a concurrent uncommitted/later TX
        if active_version and active_version.created_tx_id > tx_id:
            print(f" [CONFLICT] Tx-{tx_id} aborted write on '{key}': Overwritten by Tx-{active_version.created_tx_id}")
            raise RuntimeError(f"Write-write conflict on key '{key}'")

        if active_version:
            active_version.expired_tx_id = tx_id

        new_version = RowVersion(key, value, created_tx_id=tx_id)
        self._table[key].append(new_version)
        print(f" [WRITE] Tx-{tx_id} staged version for '{key}' = '{value}'")

    def commit(self, tx_id):
        """Finalizes transaction state."""
        if tx_id in self._active_transactions:
            self._active_transactions.remove(tx_id)
            print(f"[COMMIT] Transaction Tx-{tx_id} successfully committed.\n")


if __name__ == "__main__":
    print("--- Database Internals: MVCC Snapshot Isolation Engine ---\n")

    mvcc = MVCCStorageEngine()

    # Step 1: Initial setup transaction
    tx0 = mvcc.begin_transaction()
    mvcc.write(tx0, "account:101", 1000)
    mvcc.commit(tx0)

    # Step 2: Tx1 starts and reads original state
    tx1 = mvcc.begin_transaction()
    mvcc.read(tx1, "account:101")

    # Step 3: Concurrent Tx2 starts, modifies record, and commits
    tx2 = mvcc.begin_transaction()
    mvcc.write(tx2, "account:101", 1500)
    mvcc.commit(tx2)

    # Step 4: Tx1 reads again (Snapshot Isolation ensures it still sees 1000, not 1500!)
    print("Demonstrating Repeatable Read / Snapshot Isolation:")
    mvcc.read(tx1, "account:101")
    mvcc.commit(tx1)

    # Step 5: New Tx3 sees latest committed state (1500)
    tx3 = mvcc.begin_transaction()
    mvcc.read(tx3, "account:101")
    mvcc.commit(tx3)