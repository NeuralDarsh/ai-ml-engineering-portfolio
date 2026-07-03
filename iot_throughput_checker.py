# Implementing data conversion logic to evaluate bandwidth saturation rates

def evaluate_network_throughput(raw_bytes_received, duration_seconds, bandwidth_limit_mbps):
    """
    Converts raw bytes into Megabits per second (Mbps) to compute throughput metrics.
    Formula: Megabits = (Bytes * 8) / 1,000,000
    Throughput = Megabits / Duration
    """
    print("---  IoT Telemetry: Gateway Throughput Checker ---")
    
    # 1. Convert raw byte ingestion data into megabits
    total_bits = raw_bytes_received * 8
    total_megabits = total_bits / 1_000_000
    
    # 2. Compute throughput rate speed (Mbps)
    throughput_mbps = total_megabits / duration_seconds
    
    # 3. Calculate hardware network capacity saturation percentage
    saturation_rate = (throughput_mbps / bandwidth_limit_mbps) * 100
    
    print(f"Monitoring Duration : {duration_seconds} seconds")
    print(f"Data Processed      : {total_megabits:.2f} Mb")
    print(f"Current Data Speed  : {throughput_mbps:.2f} Mbps")
    print(f"Channel Saturation  : {saturation_rate:.1f}% of {bandwidth_limit_mbps} Mbps limit\n")
    
    # 4. Production Load-Router Alert System
    if saturation_rate >= 85.0:
        return " CRITICAL LOAD: Bandwidth limits near exhaustion. Initialize gateway network rerouting."
    elif 50.0 <= saturation_rate < 85.0:
        return " TRAFFIC WARNING: Elevated link congestion. Throttle non-essential telemetry packets."
    else:
        return " CHANNEL STABLE: Operational gateway bandwidth is within optimal parameters."

if __name__ == "__main__":
    # Simulated 10-second industrial data stream sample window
    # Inputs: Raw Bytes (approx 93.75 MB), Duration (10s), Max Allocation Limit (100 Mbps)
    simulated_bytes = 93_750_000  
    time_window = 10              
    max_gateway_capacity = 100   
    
    network_verdict = evaluate_network_throughput(simulated_bytes, time_window, max_gateway_capacity)
    print(f"Network Engineering Verdict: {network_verdict}")