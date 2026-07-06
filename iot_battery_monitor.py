# Calculating consumption slopes over time intervals to flag hardware cell anomalies

def analyze_battery_degradation(voltage_telemetry, tracking_interval_hours):
    """
    Evaluates historical voltage drops to compute hourly discharge rates.
    Flags accelerated cell depletion trends based on enterprise threshold limits.
    """
    print("---  IoT Telemetry Engine: Battery Discharge Monitor ---")
    
    total_records = len(voltage_telemetry)
    if total_records < 2:
        print("   ERROR: Insufficient telemetry data points to establish a consumption delta.")
        return None
        
    # 1. Compute total voltage drop across the complete tracking sequence
    initial_voltage = voltage_telemetry[0]
    final_voltage = voltage_telemetry[-1]
    total_drop = initial_voltage - final_voltage
    
    # 2. Calculate linear hourly degradation rate slope
    total_time = (total_records - 1) * tracking_interval_hours
    hourly_discharge_rate = total_drop / total_time if total_time > 0 else 0.0
    
    print(f"Monitoring Period  : {total_time} Hours total")
    print(f"Voltage Trajectory : {initial_voltage}V -> {final_voltage}V (Total Delta: {total_drop:.2f}V)")
    print(f"Mean Discharge Rate: {hourly_discharge_rate:.4f} V/Hour\n")
    
    # 3. Enterprise Safety Threshold Logic Layer (Max safe limit set to 0.05 V/Hour)
    CRITICAL_LIMIT = 0.05
    
    print(" Diagnostics Evaluation Verdict:")
    if hourly_discharge_rate > CRITICAL_LIMIT:
        return f" CRITICAL ALARM: Accelerated discharge detected ({hourly_discharge_rate:.4f} V/H). Schedule hardware maintenance."
    elif hourly_discharge_rate >= 0.02:
        return f" PERFORMANCE WARN: Moderate operational drawdown. Optimize edge device sleep-cycle pings."
    else:
        return " POWER HEALTHY: Battery depletion slope remains safely within optimal limits."

if __name__ == "__main__":
    # Simulated voltage timeline log for a smart sensor array taken at 2-hour intervals
    # Lithium-ion standard drop curve baseline mixed with an aggressive cell short-circuit scenario
    simulated_voltage_stream = [4.20, 4.12, 4.02, 3.82, 3.50, 2.95]
    time_step_gap = 2
    
    diagnostic_report = analyze_battery_degradation(simulated_voltage_stream, tracking_interval_hours=time_step_gap)
    print(f"Hardware Status: {diagnostic_report}")