# Distributed Systems & Message Queues: Managing worker retries and quarantining poison messages to prevent queue stalling

import time
import json
from collections import deque

class DeadLetterQueueManager:
    """
    Simulates a message broker queue worker that processes jobs, tracks failure counts,
    and isolates unprocessable messages into a Dead Letter Queue (DLQ) after exceeding max retries.
    """
    def _init_(self, max_delivery_attempts=3):
        self.max_delivery_attempts = max_delivery_attempts
        self.primary_queue = deque()
        self.dead_letter_queue = []
        self.message_attempts = {}

    def enqueue_message(self, message_id, payload):
        """Pushes a new message onto the primary processing queue."""
        self.primary_queue.append({"id": message_id, "payload": payload})
        self.message_attempts[message_id] = 0

    def process_queue(self, handler_callable):
        """Processes messages sequentially, executing handler and isolating poison pills."""
        print("--- Systems Engineering: Message Queue & DLQ Processor ---")
        print(f"Queue Size: {len(self.primary_queue)} | Max Allowed Retries: {self.max_delivery_attempts}\n")

        while self.primary_queue:
            msg = self.primary_queue.popleft()
            msg_id = msg["id"]
            self.message_attempts[msg_id] += 1
            current_attempt = self.message_attempts[msg_id]

            print(f"Processing [{msg_id}] (Attempt {current_attempt}/{self.max_delivery_attempts})")

            try:
                handler_callable(msg["payload"])
                print(f" ACK: [{msg_id}] processed successfully.\n")
            except Exception as err:
                print(f" NACK: Handler failed on [{msg_id}]: {err}")

                if current_attempt >= self.max_delivery_attempts:
                    print(f"QUARANTINED: [{msg_id}] exceeded retry limits -> Routed to Dead Letter Queue (DLQ).\n")
                    self.dead_letter_queue.append({
                        "message": msg,
                        "quarantined_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "total_attempts": current_attempt,
                        "failure_reason": str(err)
                    })
                else:
                    print(f" RE-ENQUEUED: [{msg_id}] placed back on queue for retry.\n")
                    self.primary_queue.append(msg)

        return self.get_audit_report()

    def get_audit_report(self):
        """Generates a summary of quarantined messages in the DLQ."""
        print("Queue Processing Audit Summary:")
        print(f" Primary Queue Remaining : {len(self.primary_queue)}")
        print(f" DLQ Quarantined Messages: {len(self.dead_letter_queue)}")
        if self.dead_letter_queue:
            print("\nDead Letter Queue Inspector:")
            print(json.dumps(self.dead_letter_queue, indent=2))
        return self.dead_letter_queue

if __name__ == "_main_":
    manager = DeadLetterQueueManager(max_delivery_attempts=3)

    # 1. Enqueue valid and corrupted messages
    manager.enqueue_message("msg_001", {"event": "user_signup", "user_id": 401})
    manager.enqueue_message("msg_002_corrupt", {"event": "payment_sync", "amount": None})  # Poison pill
    manager.enqueue_message("msg_003", {"event": "email_notification", "email": "dev@example.com"})

    # 2. Define handler that throws an error on invalid amount
    def sample_worker_handler(payload):
        if payload.get("event") == "payment_sync" and payload.get("amount") is None:
            raise ValueError("Malformed Payload: 'amount' field cannot be None")
        return True

    # 3. Process primary queue and inspect DLQ routing
    manager.process_queue(sample_worker_handler)