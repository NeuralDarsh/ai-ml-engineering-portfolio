# Software Architecture & DevOps: Parsing SemVer strings and evaluating backwards compatibility

import re

class SemVerChecker:
    """
    Parses Semantic Versioning strings (MAJOR.MINOR.PATCH) and audits
    compatibility between baseline and target API dependency versions.
    """
    SEMVER_PATTERN = r"^v?(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?$"

    def parse_version(self, version_str):
        """Parses a version string into a dictionary of integer components."""
        match = re.match(self.SEMVER_PATTERN, version_str.strip())
        if not match:
            raise ValueError(f"Invalid SemVer string format: '{version_str}'")

        major, minor, patch, prerelease = match.groups()
        return {
            "major": int(major),
            "minor": int(minor),
            "patch": int(patch),
            "prerelease": prerelease,
            "tuple": (int(major), int(minor), int(patch))
        }

    def check_compatibility(self, current_ver_str, target_ver_str):
        """
        Evaluates compatibility between two API versions:
        - Patch Bump: Non-breaking bug fix (100% compatible)
        - Minor Bump: Backwards-compatible new feature (Compatible)
        - Major Bump: Breaking changes detected (Incompatible)
        - Downgrade: Target version is older than current version
        """
        current = self.parse_version(current_ver_str)
        target = self.parse_version(target_ver_str)

        print("--- DevOps: Semantic Version Compatibility Auditor ---")
        print(f"Current Version : {current_ver_str} -> {current['tuple']}")
        print(f"Target Version  : {target_ver_str} -> {target['tuple']}\n")

        if target["tuple"] < current["tuple"]:
            verdict = "DOWNGRADE"
            description = "Target version is older than active version. Risk of regressions."
        elif target["major"] > current["major"]:
            verdict = "BREAKING_CHANGE"
            description = "Major version bump detected. Backwards compatibility is NOT guaranteed."
        elif target["minor"] > current["minor"]:
            verdict = "COMPATIBLE_FEATURE"
            description = "Minor version bump. Backwards-compatible features added safely."
        elif target["patch"] > current["patch"]:
            verdict = "COMPATIBLE_PATCH"
            description = "Patch version bump. Backwards-compatible bug fix applied."
        else:
            verdict = "IDENTICAL"
            description = "Target version is identical to current version."

        print("Compatibility Audit Report:")
        print(f" Status Code : {verdict}")
        print(f"  Details     : {description}")

        is_safe = verdict in ["COMPATIBLE_PATCH", "COMPATIBLE_FEATURE", "IDENTICAL"]
        print(f" Pipeline Safe: {'YES' if is_safe else 'NO (Manual Review Required)'}\n")

        return {"status": verdict, "is_safe": is_safe, "details": description}

if __name__ == "__main__":
    checker = SemVerChecker()

    # Case A: Safe minor upgrade
    checker.check_compatibility("v1.2.4", "v1.3.0")

    print("=" * 60 + "\n")

    # Case B: Breaking major upgrade
    checker.check_compatibility("v1.4.2", "v2.0.0")