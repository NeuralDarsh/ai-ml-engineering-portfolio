# Distributed Systems Engineering: Simulating network request retries with exponential backoff and jitter

import time
import random

def execute_with_exponential_backoff(operation_func, max_retries=4, base_delay=1.0, max_delay=16.0):
    """
    Executes an operation function with dynamic exponential backoff and full jitter
    to handle transient errors safely without overwhelming downstream services.
    """
    print("--- Systems Engineering: Exponential Backoff & Retry Simulator ---")
    print(f"Configuration: Max Retries={max_retries}, Base Delay={base_delay}s, Max Delay={max_delay}s\n")
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"[Attempt {attempt}/{max_retries}] Executing network operation...")
            result = operation_func(attempt)
            print(f" SUCCESS: Operation completed successfully on attempt {attempt}!\n")
            return result
        except Exception as err:
            print(f" TRANSIENT FAILURE: {err}")
            
            if attempt == max_retries:
                print(f"\n RETRY EXHAUSTED: Operation failed after {max_retries} attempts.")
                raise err
                
            # 1. Calculate Exponential Backoff delay: base * 2^(attempt - 1)
            calculated_backoff = min(max_delay, base_delay * (2 ** (attempt - 1)))
            
            # 2. Apply Full Jitter (random uniform value between 0 and calculated_backoff)
            jittered_sleep = random.uniform(0.5, calculated_backoff)
            
            print(f" Exponential Ceiling: {calculated_backoff:.2f}s | Jittered Wait: {jittered_sleep:.2f}s")
            print(f" Sleeping for {jittered_sleep:.2f} seconds before retry...\n")
            time.sleep(jittered_sleep)

if __name__ == "__main__":
    # Simulated unstable API endpoint that fails twice before succeeding on attempt 3
    def mock_unstable_api_call(attempt_number):
        if attempt_number < 3:
            raise ConnectionResetError("503 Service Unavailable: Remote server busy")
        return {"status": 200, "message": "Payload processed successfully"}
    
    execute_with_exponential_backoff(mock_unstable_api_call, max_retries=4)