# Software Engineering & DevOps: Contextual feature flag evaluation, user targeting, and deterministic percentage rollouts

import hashlib
import json

class FeatureFlagEvaluator:
    """
    Evaluates dynamic feature flags based on global switches,
    allowlisted accounts, and deterministic percentage rollouts.
    """
    def __init__(self, flag_configurations=None):
        self.flags = flag_configurations or {}

    def _hash_percentage(self, entity_key, flag_name):
        """Generates a deterministic integer between 0 and 99 using MD5."""
        combined = f"{entity_key}:{flag_name}".encode("utf-8")
        hex_digest = hashlib.md5(combined).hexdigest()
        return int(hex_digest[:6], 16) % 100

    def is_enabled(self, flag_name, user_context=None):
        user_context = user_context or {}
        user_id = user_context.get("user_id", "anonymous")
        tier = user_context.get("tier", "standard")

        flag = self.flags.get(flag_name)
        if not flag:
            print(f" FLAG NOT FOUND: '{flag_name}' defaulting to False.")
            return False

        # 1. Check global master switch
        if not flag.get("enabled", False):
            print(f" FLAG DISABLED: '{flag_name}' is globally turned off.")
            return False

        # 2. Check allowlisted target users
        if user_id in flag.get("allowlisted_users", []):
            print(f" ALLOWLIST MATCH: User '{user_id}' explicitly granted access to '{flag_name}'.")
            return True

        # 3. Check allowed account tiers
        if tier in flag.get("allowed_tiers", []):
            print(f" TIER MATCH: Tier '{tier}' granted access to '{flag_name}'.")
            return True

        # 4. Check percentage rollout
        rollout_percentage = flag.get("rollout_percentage", 0)
        user_bucket = self._hash_percentage(user_id, flag_name)

        if user_bucket < rollout_percentage:
            print(f" ROLLOUT INCLUDED: User '{user_id}' (Bucket: {user_bucket}) falls within {rollout_percentage}% rollout.")
            return True
        else:
            print(f" ROLLOUT EXCLUDED: User '{user_id}' (Bucket: {user_bucket}) falls outside {rollout_percentage}% rollout.")
            return False

if __name__ == "__main__":
    print("--- DevOps: Feature Flag & Rollout Rule Evaluator ---\n")

    # Sample configurations for production flags
    sample_flags = {
        "v2_neural_search": {
            "enabled": True,
            "rollout_percentage": 50,
            "allowlisted_users": ["user_darshan_dev"],
            "allowed_tiers": ["enterprise"]
        },
        "beta_dark_mode": {
            "enabled": False,
            "rollout_percentage": 100,
            "allowlisted_users": [],
            "allowed_tiers": []
        }
    }

    evaluator = FeatureFlagEvaluator(sample_flags)

    # Test Case 1: Allowlisted user
    print("Test 1: Allowlisted Admin/Dev User")
    evaluator.is_enabled("v2_neural_search", {"user_id": "user_darshan_dev", "tier": "standard"})

    print("\n" + "=" * 50 + "\n")

    # Test Case 2: Standard user tested against 50% rollout
    print("Test 2: Standard User Rollout Evaluation")
    evaluator.is_enabled("v2_neural_search", {"user_id": "user_10283", "tier": "standard"})

    print("\n" + "=" * 50 + "\n")

    # Test Case 3: Globally disabled flag
    print("Test 3: Globally Disabled Feature")
    evaluator.is_enabled("beta_dark_mode", {"user_id": "user_10283", "tier": "enterprise"})