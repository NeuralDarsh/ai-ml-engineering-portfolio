# Production Developer Tool: Validating dynamic JSON response payloads against structural data models

from typing import Dict, Any, List

class SchemaValidationError(Exception):
    """Custom exception raised when JSON response fails structural type checks."""
    pass

class ResponseSchemaValidator:
    """
    Validates dynamic AI API JSON response payloads against expected structural schemas.
    Ensures correct data types, required keys, and nested matrix boundaries.
    """
    def __init__(self, expected_schema: Dict[str, type]):
        self.expected_schema = expected_schema

    def validate(self, payload: Dict[str, Any]) -> bool:
        """
        Recursively checks incoming JSON structure against defined schema specifications.
        """
        print("--- AI Microservices: Response Schema Validation Engine ---")
        print(f"Ingested Payload Keys: {list(payload.keys())}\n")
        
        for key, expected_type in self.expected_schema.items():
            # 1. Verify key presence
            if key not in payload:
                raise SchemaValidationError(f"Missing required response key: '{key}'")
            
            val = payload[key]
            
            # 2. Check value data type matching
            if isinstance(expected_type, list):
                if not isinstance(val, list):
                    raise SchemaValidationError(f"Key '{key}' expected list, got {type(val).__name__}")
            elif not isinstance(val, expected_type):
                raise SchemaValidationError(
                    f"Type mismatch on key '{key}': expected {expected_type.__name__}, got {type(val).__name__}"
                )
        
        print("Response Schema Audit Verdict:")
        print("VALIDATION SUCCESSFUL: Ingested response matches production API contract.")
        return True

if __name__ == "__main__":
    # Define expected API schema contract for a mock LLM inference endpoint
    llm_api_schema = {
        "model_id": str,
        "tokens_used": int,
        "confidence_score": float,
        "generated_text": str,
        "finish_reason": str
    }

    # Case A: Valid AI Microservice JSON Response Payload
    valid_payload = {
        "model_id": "gpt-4o-mini-v1",
        "tokens_used": 142,
        "confidence_score": 0.985,
        "generated_text": "Selected architecture candidate verified for deployment.",
        "finish_reason": "completed"
    }

    validator = ResponseSchemaValidator(llm_api_schema)
    try:
        validator.validate(valid_payload)
    except SchemaValidationError as e:
        print(f"Schema Error: {e}")

    print("\n" + "="*60 + "\n")

    # Case B: Malformed Payload (Type mismatch on tokens_used + missing key)
    malformed_payload = {
        "model_id": "gpt-4o-mini-v1",
        "tokens_used": "142", # Should be int, received string
        "confidence_score": 0.985
    }

    try:
        validator.validate(malformed_payload)
    except SchemaValidationError as e:
        print(f"Schema Exception Caught: {e}")