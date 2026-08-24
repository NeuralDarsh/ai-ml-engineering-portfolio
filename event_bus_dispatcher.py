# Distributed Systems Architecture: Decoupling microservice communication via topic-based publish-subscribe event routing

import time
import json
from collections import defaultdict

class EventBusDispatcher:
    """
    A lightweight, in-process Event Bus implementing the Pub/Sub pattern.
    Supports topic subscriptions, wildcard topic matching, and safe event dispatching.
    """
    def __init__(self):
        # Maps topic -> list of subscriber callbacks
        self._subscribers = defaultdict(list)

    def subscribe(self, topic, handler_callable):
        """Subscribes a callback handler to a specific topic."""
        self._subscribers[topic].append(handler_callable)
        print(f"SUBSCRIBED: Handler '{handler_callable.__name__}' -> Topic '{topic}'")

    def publish(self, topic, payload):
        """
        Publishes an event payload to a topic, executing all exact-match
        and wildcard ('*') subscriber callbacks safely.
        """
        print(f"\n--- Event Bus: Publishing to Topic '{topic}' ---")
        event_message = {
            "topic": topic,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "payload": payload
        }

        matched_handlers = list(self._subscribers.get(topic, []))
        
        # Include global wildcard subscribers
        if "*" in self._subscribers and topic != "*":
            matched_handlers.extend(self._subscribers["*"])

        if not matched_handlers:
            print(f" NO SUBSCRIBERS: Message dropped for topic '{topic}'.")
            return 0

        dispatched_count = 0
        for handler in matched_handlers:
            try:
                handler(event_message)
                dispatched_count += 1
            except Exception as err:
                print(f"HANDLER ERROR: '{handler.__name__}' failed on topic '{topic}': {err}")

        print(f"DISPATCH COMPLETE: Dispatched to {dispatched_count} subscriber(s).\n")
        return dispatched_count

if __name__ == "__main__":
    bus = EventBusDispatcher()

    # Define subscriber listener callbacks
    def email_notifier(event):
        print(f"  [EmailService] Sending welcome email to: {event['payload'].get('email')}")

    def audit_logger(event):
        print(f"  [AuditLog] Ingested event on [{event['topic']}]: {json.dumps(event['payload'])}")

    def analytics_tracker(event):
        print(f"  [Analytics] Incrementing metric for: {event['payload'].get('action')}")

    # 1. Register subscriptions
    print("Registering Service Subscriptions:")
    bus.subscribe("user.created", email_notifier)
    bus.subscribe("user.created", audit_logger)
    bus.subscribe("payment.processed", analytics_tracker)
    bus.subscribe("*", lambda evt: print(f" [GlobalMonitor] Caught event: {evt['topic']}"))

    # 2. Publish sample events
    bus.publish("user.created", {"user_id": 9012, "email": "darshan.dev@example.com", "action": "signup"})
    bus.publish("payment.processed", {"order_id": "ord_8871", "amount": 120.50, "action": "checkout"})