# Developer Automation: Monitoring network endpoint stability and measuring transmission delay

import urllib.request
import time

def audit_api_endpoints(endpoint_directory):
    """
    Pings a structured checklist of web targets, measures response performance metrics,
    and isolates degraded or broken web connection routes.
    """
    print("--- Developer Tools: Automated Web API Status Auditor ---\n")
    
    status_summary = {}
    
    for service_name, url in endpoint_directory.items():
        print(f"Testing Connectivity Profile: {service_name}...")
        
        start_clock = time.time()
        try:
            # Send an HTTP request with a strict 3-second timeout guardrail
            response = urllib.request.urlopen(url, timeout=3.0)
            elapsed_latency = time.time() - start_clock
            status_code = response.getcode()
            
            status_summary[service_name] = {
                "status": "ONLINE",
                "code": status_code,
                "latency_ms": round(elapsed_latency * 1000, 2)
            }
            print(f"  Connected to {service_name} | Response: {status_code} | Latency: {status_summary[service_name]['latency_ms']} ms")
            
        except urllib.error.HTTPError as http_err:
            elapsed_latency = time.time() - start_clock
            status_summary[service_name] = {
                "status": "DEGRADED",
                "code": http_err.code,
                "latency_ms": round(elapsed_latency * 1000, 2)
            }
            print(f" HTTP Error Intercepted on {service_name} | Code: {http_err.code}")
            
        except Exception as general_err:
            status_summary[service_name] = {
                "status": " OFFLINE / UNREACHABLE",
                "code": "NONE",
                "latency_ms": -1.0
            }
            print(f" Connection Failure on {service_name} | Reason: {general_err}")
            
    print("\n Web Infrastructure Audit Complete.")
    return status_summary

if __name__ == "__main__":
    # A checklist of standard, highly stable test and public API endpoint URLs
    target_endpoints = {
        "GitHub Public API Gateway": "https://api.github.com",
        "HTTPBin Test Server Engine": "https://httpbin.org/get",
        "Mozilla Network Diagnostics": "https://httpbin.org/status/200",
        "Simulated Corrupt URL Link" : "https://invalid.endpoint.test-fail"
    }
    
    # Run the automated network validation test pipeline
    audit_results = audit_api_endpoints(target_endpoints)