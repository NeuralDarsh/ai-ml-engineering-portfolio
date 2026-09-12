# Message Queues & Microservice Resilience: Handling transient failures and offloading unprocessable poison messages

import time
import json

class MessageTask:
    """Represents a queued task payload with retry metadata."""
    def __init__(self, task_id, payload, max_retries=3):
        self.task_id = task_id
        self.payload = payload
        self.max_retries = max_retries
        self.retry_count = 0
        self.last_error = None


class DeadLetterQueueEngine:
    """
    Simulates a message processing engine equipped with exponential backoff retries
    and automated routing to a Dead Letter Queue (DLQ) upon exceeding max retry attempts.
    """
    def __init__(self, base_delay=0.1):
        self.base_delay = base_delay
        self.dead_letter_queue = []
        self.completed_tasks = []

    def process_task(self, task, worker_callable):
        """Processes a task, triggering exponential retries or DLQ offload on persistent errors."""
        print(f"--- Queue Processor: Task '{task.task_id}' (Attempt: {task.retry_count + 1}) ---")

        while task.retry_count <= task.max_retries:
            try:
                print(f"Executing worker logic for task '{task.task_id}'...")
                result = worker_callable(task.payload)
                self.completed_tasks.append({"task_id": task.task_id, "result": result})
                print(f"SUCCESS: Task '{task.task_id}' processed successfully.\n")
                return True
            except Exception as err:
                task.retry_count += 1
                task.last_error = str(err)
                print(f"EXECUTION ERROR: {err}")

                if task.retry_count <= task.max_retries:
                    # Exponential backoff delay: base * (2 ** retry)
                    delay = self.base_delay * (2 ** (task.retry_count - 1))
                    print(f"[BACKOFF RETRY] Retrying in {delay:.2f}s (Retry {task.retry_count}/{task.max_retries})...\n")
                    time.sleep(delay)
                else:
                    # Max retries exceeded -> Route to DLQ
                    self._route_to_dlq(task)
                    return False

    def _route_to_dlq(self, task):
        """Offloads failed task to Dead Letter Queue with execution diagnostics."""
        dlq_entry = {
            "task_id": task.task_id,
            "payload": task.payload,
            "failed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_attempts": task.retry_count,
            "error_reason": task.last_error
        }
        self.dead_letter_queue.append(dlq_entry)
        print(f"[DLQ OFFLOAD] Task '{task.task_id}' exceeded max retries! Moved to Dead Letter Queue.\n")


if __name__ == "__main__":
    print("--- Messaging Resilience: DLQ & Retry Policy Engine ---\n")

    engine = DeadLetterQueueEngine(base_delay=0.1)

    # Simulated worker that handles payments
    def simulated_payment_handler(payload):
        # Poison-pill payload with invalid currency
        if payload.get("currency") not in ["USD", "JPY", "INR"]:
            raise ValueError(f"Unsupported currency: '{payload.get('currency')}'")
        return {"status": "PAID", "ref": f"pay_{payload['order_id']}"}

    # 1. Healthy Task
    task_healthy = MessageTask("task_1001", {"order_id": "ord_551", "currency": "JPY", "amount": 2500})
    engine.process_task(task_healthy, simulated_payment_handler)

    # 2. Poison-Pill Task (Simulates corrupted input or permanent downstream rejection)
    task_poison = MessageTask("task_1002", {"order_id": "ord_552", "currency": "XYZ", "amount": 100}, max_retries=3)
    engine.process_task(task_poison, simulated_payment_handler)

    # 3. Inspect DLQ Storage
    print("Final Dead Letter Queue (DLQ) State:")
    print(json.dumps(engine.dead_letter_queue, indent=2))