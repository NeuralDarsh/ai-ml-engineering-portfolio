# Distributed Systems & Data Consistency: Eliminating dual-write race conditions using transactional outbox tables and relay dispatchers

import time
import json
import uuid

class MockDatabase:
    """Simulates an ACID-compliant database holding application entities and an outbox table."""
    def __init__(self):
        self.orders = {}
        self.outbox = []

    def execute_transactional_write(self, order_id, order_data):
        """
        Atomically saves both business entity mutation and outbox event
        in a single simulated transaction.
        """
        # 1. Mutate business state
        self.orders[order_id] = order_data

        # 2. Append event to outbox table within same commit
        event_record = {
            "event_id": f"evt_{uuid.uuid4().hex[:8]}",
            "aggregate_type": "Order",
            "aggregate_id": order_id,
            "event_type": "OrderCreated",
            "payload": order_data,
            "status": "PENDING",  # PENDING -> PUBLISHED
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.outbox.append(event_record)
        print(f" [DB TX COMMIT] Order '{order_id}' persisted and outbox record queued.")
        return event_record["event_id"]


class OutboxRelayDispatcher:
    """
    Simulates a background CDC (Change Data Capture) polling worker that
    tails the outbox table, publishes pending records to a broker, and marks them PUBLISHED.
    """
    def __init__(self, db, broker_callable):
        self.db = db
        self.broker_callable = broker_callable

    def poll_and_dispatch(self):
        """Scans outbox table for PENDING messages and dispatches them safely."""
        print("\n--- Outbox Relay Worker: Polling for Pending Events ---")
        pending_events = [e for e in self.db.outbox if e["status"] == "PENDING"]

        if not pending_events:
            print("No pending events to dispatch.")
            return 0

        dispatched_count = 0
        for event in pending_events:
            print(f"Dispatching Event [{event['event_id']}] -> Type: '{event['event_type']}'")
            try:
                # Dispatch to external broker
                ack = self.broker_callable(event)
                if ack:
                    event["status"] = "PUBLISHED"
                    event["published_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                    dispatched_count += 1
                    print(f" ACK RECEIVED: Event [{event['event_id']}] marked PUBLISHED.\n")
                else:
                    print(f"NACK: Broker rejected event [{event['event_id']}]. Keeping PENDING.\n")
            except Exception as err:
                print(f" RELAY ERROR: Failed sending [{event['event_id']}]: {err}. Retrying next cycle.\n")

        return dispatched_count


if __name__ == "__main__":
    print("--- Distributed Architecture: Transactional Outbox Pattern ---\n")

    db = MockDatabase()

    # Simulated Message Broker (e.g. Kafka producer callback)
    def mock_message_broker(event):
        print(f"[MessageBroker] Ingested topic '{event['aggregate_type']}Events': {json.dumps(event['payload'])}")
        return True

    relay = OutboxRelayDispatcher(db, mock_message_broker)

    # 1. Simulate API endpoint executing local atomic write
    print("Step 1: Ingesting Order Creation (Atomic Business + Outbox Write)")
    db.execute_transactional_write("ord_901", {"customer": "Darshan", "amount": 1250.0, "status": "APPROVED"})
    db.execute_transactional_write("ord_902", {"customer": "Kenji", "amount": 340.0, "status": "APPROVED"})

    # 2. Run background relay worker pass to poll and publish to broker
    relay.poll_and_dispatch()

    # 3. Verify outbox table state
    print("Final Outbox Table State:")
    print(json.dumps(db.outbox, indent=2))