# Simulating hardware data buffer thresholds under scaling data packet traffic rates

def estimate_network_congestion(packet_rates_per_sec, buffer_capacity):
    """
    Evaluates incoming IoT data streams against local gateway buffer capabilities.
    Calculates a congestion percentage index and recommends bandwidth scaling actions.
    """
    print("---  IoT Gateway Network Congestion Estimator ---")
    
    # 1. Compute traffic aggregations
    total_intervals = len(packet_rates_per_sec)
    average_traffic_load = sum(packet_rates_per_sec) / total_intervals
    peak_traffic_load = max(packet_rates_per_sec)
    
    # 2. Compute the Congestion Index Ratio based on peak load capacity
    congestion_ratio = (peak_traffic_load / buffer_capacity) * 100
    final_index = min(100.0, congestion_ratio)
    
    print(f"Monitoring Windows: {total_intervals} seconds")
    print(f"Average Packet Ingestion: {average_traffic_load:.1f} packets/sec")
    print(f"Peak Stress Traffic Load: {peak_traffic_load} packets/sec")
    print(f"Calculated Congestion Index: {final_index:.1f}%\n")
    
    # 3. Decision Matrix Router
    if final_index >= 85.0:
        return " CRITICAL: Buffer overflow risk detected. Deploy additional IoT network gateways."
    elif 50.0 <= final_index < 85.0:
        return " WARNING: Moderate traffic congestion. Enable packet deduplication queues."
    else:
        return " STABLE: Network buffer overhead is healthy for current load."

if __name__ == "__main__":
    # Simulated log showing incoming packets per second over a 6-second window
    # Gateway router hardware buffer capability maximum threshold limit is set to 150 packets/sec
    simulated_traffic_stream = [85, 110, 142, 95, 78, 120]
    hardware_buffer_limit = 150
    
    verdict = estimate_network_congestion(simulated_traffic_stream, hardware_buffer_limit)
    print(f"Network Engineering Verdict: {verdict}")