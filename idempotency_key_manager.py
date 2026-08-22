# Distributed Systems & API Reliability: Preventing duplicate request execution using idempotent keys and cached response replays

import time
import json

class IdempotencyKeyManager:
    """
    Tracks operation execution state per Idempotency-Key.
    Caches responses to return deterministic replays for duplicate requests and prevent duplicate processing.
    """
    def __init__(self, ttl_seconds=10.0):
        self.ttl_seconds = ttl_seconds
        # Maps key -> {"status": "IN_PROGRESS"|"COMPLETED", "response": dict, "created_at": float}
        self.storage = {}

    def _purge_expired(self):
        """Removes expired keys outside the TTL window."""
        now = time.time()
        expired = [k for k, v in self.storage.items() if now - v["created_at"] > self.ttl_seconds]
        for k in expired:
            del self.storage[k]

    def execute_idempotent(self, idempotency_key, action_callable, *args, **kwargs):
        """
        Executes action only if the key has not been processed.
        Returns cached response on duplicate attempts.
        """
        self._purge_expired()
        now = time.time()

        print(f"--- Systems Engineering: Idempotency Key Gateway ---")
        print(f"Received Request with Idempotency-Key: '{idempotency_key}'")

        if idempotency_key in self.storage:
            entry = self.storage[idempotency_key]
            if entry["status"] == "COMPLETED":
                print(f"  DUPLICATE DETECTED: Returning cached original response (Bypassed execution).")
                print(f"  Replayed Payload: {json.dumps(entry['response'], indent=2)}\n")
                return entry["response"]
            elif entry["status"] == "IN_PROGRESS":
                print(f"  CONFLICT: Request with key '{idempotency_key}' is currently in progress.\n")
                return {"status": 409, "error": "Concurrent request in progress"}

        # Mark as IN_PROGRESS
        self.storage[idempotency_key] = {"status": "IN_PROGRESS", "response": None, "created_at": now}

        try:
            print("FIRST ATTEMPT: Executing downstream operation logic...")
            result = action_callable(*args, **kwargs)
            self.storage[idempotency_key]["status"] = "COMPLETED"
            self.storage[idempotency_key]["response"] = result
            print(f"SUCCESS: Executed and stored in idempotency cache.")
            print(f"Response Payload: {json.dumps(result, indent=2)}\n")
            return result
        except Exception as err:
            del self.storage[idempotency_key]
            print(f"ERROR: Execution failed. Key released for retry: {err}\n")
            raise err

if __name__ == "__main__":
    manager = IdempotencyKeyManager(ttl_seconds=5.0)

    # Simulated payment processor action
    def process_payment(account_id, amount):
        return {
            "transaction_id": f"txn_{int(time.time() * 1000)}",
            "account_id": account_id,
            "amount_charged": amount,
            "status": "PAID"
        }

    idempotency_token = "req_order_99812_unique"

    # 1. First invocation: Executes business logic
    print("Test 1: Initial Inbound Request")
    manager.execute_idempotent(idempotency_token, process_payment, "acc_401", 1500.00)

    # 2. Duplicate retry with same token: Replays cached response without re-charging
    print("Test 2: Duplicate Inbound Retry (Network timeout retry)")
    manager.execute_idempotent(idempotency_token, process_payment, "acc_401", 1500.00)