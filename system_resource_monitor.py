# System Utility: Auditing local storage capacity ratios and triggering threshold alerts

import shutil
import os

def audit_system_storage(target_path="."):
    """
    Evaluates disk usage metrics for a given target filesystem directory path,
    calculates storage usage percentages, and returns a system health verdict.
    """
    print("--- System Tools: Disk & Resource Health Monitor ---")
    print(f"Auditing Path Context: {os.path.abspath(target_path)}\n")
    
    try:
        # Get storage usage stats (returned in bytes)
        total_bytes, used_bytes, free_bytes = shutil.disk_usage(target_path)
        
        # Convert bytes to Gigabytes (GB)
        gb_conversion = 1024 ** 3
        total_gb = total_bytes / gb_conversion
        used_gb = used_bytes / gb_conversion
        free_gb = free_bytes / gb_conversion
        
        # Compute usage percentage
        used_percentage = (used_bytes / total_bytes) * 100
        
        print("Storage Resource Audit Metrics:")
        print(f"Total Space Allocated : {total_gb:.2f} GB")
        print(f"Consumed Space        : {used_gb:.2f} GB ({used_percentage:.1f}%)")
        print(f"Free Available Space  : {free_gb:.2f} GB")
        
        # System Health Routing Matrix
        WARNING_THRESHOLD_PERCENT = 85.0
        CRITICAL_THRESHOLD_PERCENT = 95.0
        
        if used_percentage >= CRITICAL_THRESHOLD_PERCENT:
            print(f"\n CRITICAL ALERT: Storage usage at {used_percentage:.1f}%! Immediate purge required.")
            return "CRITICAL"
        elif used_percentage >= WARNING_THRESHOLD_PERCENT:
            print(f"\n WARNING ALERT: High storage usage ({used_percentage:.1f}%). Monitor closely.")
            return "WARNING"
        else:
            print(f"\n HEALTHY: System storage capacity is optimal ({100 - used_percentage:.1f}% free).")
            return "HEALTHY"
            
    except Exception as err:
        print(f"Audit Exception Caught: {err}")
        return "ERROR"

if __name__ == "__main__":
    # Audit current workspace directory filesystem
    current_workspace = os.getcwd()
    audit_system_storage(current_workspace)