# Distributed Systems & Microservices: Coordinating multi-service workflows with automated compensating rollbacks

import time
import json

class SagaStep:
    """Represents a single forward action and its reverse compensating rollback action."""
    def __init__(self, step_name, execute_fn, compensate_fn):
        self.step_name = step_name
        self.execute_fn = execute_fn
        self.compensate_fn = compensate_fn


class SagaOrchestrator:
    """
    Executes a series of transactional steps across microservices.
    If a step fails, triggers reverse compensation rollbacks for all previously completed steps.
    """
    def __init__(self):
        self.steps = []
        self.executed_steps = []

    def add_step(self, step_name, execute_fn, compensate_fn):
        """Registers a forward execution handler alongside its compensating counterpart."""
        self.steps.append(SagaStep(step_name, execute_fn, compensate_fn))

    def execute_saga(self, saga_id, payload):
        print(f"--- Distributed Systems: Saga Orchestrator [Saga ID: {saga_id}] ---")
        print(f"Executing workflow with {len(self.steps)} transactional steps...\n")

        self.executed_steps = []

        for step in self.steps:
            print(f"[FORWARD] Executing step: '{step.step_name}'")
            try:
                success = step.execute_fn(payload)
                if not success:
                    raise RuntimeError(f"Step '{step.step_name}' reported business logic rejection.")
                self.executed_steps.append(step)
                print(f" SUCCESS: '{step.step_name}' committed.\n")
            except Exception as err:
                print(f"STEP FAILED: '{step.step_name}' -> Reason: {err}")
                self._rollback_saga(saga_id, payload)
                return {"saga_id": saga_id, "status": "COMPENSATED_AND_ROLLED_BACK", "failed_step": step.step_name}

        print(f"SAGA VERDICT: [Saga ID: {saga_id}] Completed all steps successfully.\n")
        return {"saga_id": saga_id, "status": "SUCCESS"}

    def _rollback_saga(self, saga_id, payload):
        """Executes compensating transactions in reverse order."""
        print(f"\n[ROLLBACK TRIGGERED] Initiating compensation pipeline for Saga '{saga_id}':")
        for step in reversed(self.executed_steps):
            try:
                print(f"[COMPENSATE] Rolling back step: '{step.step_name}'")
                step.compensate_fn(payload)
                print(f"  Compensation completed for '{step.step_name}'.")
            except Exception as comp_err:
                print(f"CRITICAL: Compensation failed for '{step.step_name}': {comp_err}")
        print("All executed steps reverted. System returned to clean baseline.\n")


if __name__ == "__main__":
    # Define mock service forward operations and compensations
    def reserve_inventory(data):
        print(" [InventoryService] Stock reserved for SKU:", data["sku"])
        return True

    def release_inventory(data):
        print("[InventoryService] Releasing stock back to inventory for SKU:", data["sku"])

    def charge_customer(data):
        if data["amount"] > 1000:
            raise ValueError("Insufficient balance for charge limit (> $1000).")
        print(f"[PaymentService] Charged customer ${data['amount']}")
        return True

    def refund_customer(data):
        print(f"[PaymentService] Issuing refund of ${data['amount']}")

    def schedule_dispatch(data):
        print("[ShippingService] Courier scheduled for delivery.")
        return True

    def cancel_dispatch(data):
        print("[ShippingService] Cancelling courier dispatch.")

    # 1. Setup Saga Workflow
    orchestrator = SagaOrchestrator()
    orchestrator.add_step("ReserveInventory", reserve_inventory, release_inventory)
    orchestrator.add_step("ProcessPayment", charge_customer, refund_customer)
    orchestrator.add_step("ScheduleDispatch", schedule_dispatch, cancel_dispatch)

    # Test Case 1: Successful end-to-end Saga
    print("=== TEST CASE 1: Successful Order Flow ===")
    orchestrator.execute_saga("saga_ord_101", {"sku": "A10-PRO", "amount": 250})

    print("=" * 60 + "\n")

    # Test Case 2: Failed step triggering reverse compensation rollback
    print("=== TEST CASE 2: Failed Order (Payment Exceeds Limit) ===")
    orchestrator.execute_saga("saga_ord_102", {"sku": "GPU-4090", "amount": 1600})