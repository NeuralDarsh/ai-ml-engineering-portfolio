# Distributed Systems & Microservices: Orchestrator-driven Saga pattern ensuring eventual consistency across distributed domains

import json
import uuid

class SagaStep:
    """Defines a discrete forward action and its matching semantic compensating action."""
    def __init__(self, name, forward_action, compensate_action):
        self.name = name
        self.forward_action = forward_action
        self.compensate_action = compensate_action


class SagaOrchestrator:
    """
    Coordinates forward execution of transactional microservice steps.
    Traverses in reverse to trigger compensating rollbacks if any step fails.
    """
    def __init__(self, saga_name):
        self.saga_name = saga_name
        self.steps = []
        self.completed_steps = []
        self.execution_log = []

    def add_step(self, step):
        self.steps.append(step)

    def execute(self, payload):
        saga_id = f"saga_{uuid.uuid4().hex[:8]}"
        print(f"\n--- Initiating Saga: '{self.saga_name}' [ID: {saga_id}] ---")
        self.completed_steps = []
        self.execution_log = []

        context = dict(payload)

        # 1. Forward Execution Phase
        print("[PHASE 1: FORWARD TRANSACTIONS]")
        for step in self.steps:
            print(f"Executing Step: '{step.name}'...")
            try:
                result = step.forward_action(saga_id, context)
                self.completed_steps.append(step)
                self.execution_log.append({
                    "step": step.name,
                    "action": "FORWARD",
                    "status": "SUCCESS",
                    "result": result
                })
                print(f" SUCCESS: '{step.name}' committed.")
            except Exception as err:
                print(f" FAILED: '{step.name}' encountered error: {err}")
                self.execution_log.append({
                    "step": step.name,
                    "action": "FORWARD",
                    "status": "FAILED",
                    "error": str(err)
                })
                # Trigger backward compensation
                self._compensate(saga_id, context)
                return False

        print(f"Saga '{self.saga_name}' completed successfully across all distributed services!\n")
        return True

    def _compensate(self, saga_id, context):
        """Backward traversal to execute compensating transactions."""
        print("\n[PHASE 2: COMPENSATING ROLLBACK TRANSACTIONS]")
        for step in reversed(self.completed_steps):
            print(f"Compensating Step: '{step.name}'...")
            try:
                step.compensate_action(saga_id, context)
                self.execution_log.append({
                    "step": step.name,
                    "action": "COMPENSATE",
                    "status": "SUCCESS"
                })
                print(f"ROLLED BACK: '{step.name}' compensation confirmed.")
            except Exception as comp_err:
                print(f"CRITICAL: Compensation failed for '{step.name}': {comp_err}")
                self.execution_log.append({
                    "step": step.name,
                    "action": "COMPENSATE",
                    "status": "FAILED",
                    "error": str(comp_err)
                })

        print("Saga terminated. System reconciled to a consistent baseline via compensation.\n")


if __name__ == "__main__":
    print("--- Distributed Reliability: Saga Orchestration Engine (Day 100 Finale) ---\n")

    # Mock service states
    flight_reservations = {}
    hotel_reservations = {}
    payment_ledger = {}

    # Define Service Handlers
    def reserve_flight(saga_id, ctx):
        flight_reservations[saga_id] = {"flight": ctx["flight_no"], "seat": "12A"}
        return flight_reservations[saga_id]

    def cancel_flight(saga_id, ctx):
        flight_reservations.pop(saga_id, None)

    def book_hotel(saga_id, ctx):
        hotel_reservations[saga_id] = {"hotel": ctx["hotel_name"], "nights": 3}
        return hotel_reservations[saga_id]

    def cancel_hotel(saga_id, ctx):
        hotel_reservations.pop(saga_id, None)

    def process_payment(saga_id, ctx):
        # Enforce budget constraint to test compensation
        if ctx.get("amount", 0) > 1000:
            raise ValueError(f"Credit limit exceeded: Charge of ${ctx['amount']} rejected")
        payment_ledger[saga_id] = ctx["amount"]
        return {"charged": ctx["amount"]}

    def refund_payment(saga_id, ctx):
        payment_ledger.pop(saga_id, None)

    # Build Saga Definition
    travel_saga = SagaOrchestrator("BookHolidayPackageSaga")
    travel_saga.add_step(SagaStep("FlightBookingService", reserve_flight, cancel_flight))
    travel_saga.add_step(SagaStep("HotelBookingService", book_hotel, cancel_hotel))
    travel_saga.add_step(SagaStep("PaymentProcessingService", process_payment, refund_payment))

    # Scenario 1: Successful End-to-End Saga
    print("Scenario 1: Executing Valid Saga (Within Budget):")
    travel_saga.execute({"flight_no": "NH-829", "hotel_name": "Tokyo Shinjuku Inn", "amount": 650})

    # Scenario 2: Failing Saga Triggering Backward Compensation
    print("Scenario 2: Executing Failing Saga (Payment Fails, Rollback Preceding Steps):")
    travel_saga.execute({"flight_no": "NH-830", "hotel_name": "Osaka Grand", "amount": 1800})

    print("Final Service State Audit Post-Rollback:")
    print(f"Flight Reservations : {flight_reservations}")
    print(f"Hotel Reservations  : {hotel_reservations}")
    print(f"Payment Ledger       : {payment_ledger}")