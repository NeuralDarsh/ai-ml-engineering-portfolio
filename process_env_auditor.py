# System Tooling: Auditing active process runtime metrics, platform environment, and environment flags

import os
import sys
import platform

def audit_process_environment():
    """
    Inspects active Python process context, runtime platform metadata,
    and system environment variables to generate an operational health audit.
    """
    print("--- System Tools: Process Environment & Security Context Auditor ---")
    
    # 1. Gather Process Execution Identifiers & Platform Specs
    process_id = os.getpid()
    python_version = sys.version.split()[0]
    operating_system = platform.system()
    os_release = platform.release()
    architecture = platform.machine()
    
    print("Active Process Metadata:")
    print(f"Process ID (PID)    : {process_id}")
    print(f"Python Runtime      : {python_version}")
    print(f"Operating System    : {operating_system} {os_release} ({architecture})")
    print(f"Execution Path      : {sys.executable}\n")
    
    # 2. Inspect Environment Variable Flags
    env_vars = os.environ
    total_env_keys = len(env_vars)
    
    # Search for standard execution flags
    path_set = "PATH" in env_vars
    user_name = env_vars.get("USERNAME") or env_vars.get("USER") or "Unknown User"
    
    print("Security & Environment Context:")
    print(f"Active User Context : {user_name}")
    print(f"Total Env Variables : {total_env_keys}")
    print(f"PATH Configured     : {'YES' if path_set else 'NO'}")
    
    # 3. Security Audit Verdict Matrix
    print("\n Operational Verdict:")
    if sys.version_info < (3, 8):
        print("WARNING: Deprecated Python runtime version detected. Upgrade recommended.")
        return "WARNING"
    else:
        print("HEALTHY: Process execution environment is stable and nominal.")
        return "HEALTHY"

if __name__ == "__main__":
    audit_process_environment()