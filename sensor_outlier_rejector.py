# Implementing statistical threshold guardrails to sanitize streaming hardware metrics

import numpy as np

def filter_sensor_stream(raw_readings, z_threshold=2.0):
    """
    Evaluates streaming sensor signals and filters out anomalies using Z-scores.
    Formula: Z = (X - Mean) / Std_Deviation
    """
    print("---  IoT Ingestion Pipeline: Sensor Outlier Rejector ---")
    
    # 1. Convert to NumPy vector array and calculate basic statistical properties
    data_array = np.array(raw_readings)
    mean_val = np.mean(data_array)
    std_dev = np.std(data_array)
    
    print(f"Stream Statistics -> Baseline Mean: {mean_val:.2f} | Std Dev: {std_dev:.2f}\n")
    
    clean_readings = []
    rejected_readings = []
    
    # 2. Iterate and evaluate each incoming packet data point
    for val in data_array:
        # Calculate standard deviation distance (Z-score)
        z_score = abs(val - mean_val) / std_dev if std_dev > 0 else 0.0
        
        # 3. Structural threshold filtering guardrail
        if z_score > z_threshold:
            print(f"  REJECTED: Value {val:<5} flagged as anomaly (Z-Score: {z_score:.2f})")
            rejected_readings.append(val)
        else:
            clean_readings.append(val)
            
    print(f"\n Sanitization Report:")
    print(f"  Accepted Production Elements: {clean_readings}")
    print(f"  Isolated Outlier Anomalies  : {rejected_readings}")
    return clean_readings

if __name__ == "__main__":
    # Simulated factory temperature log sensor readings (°C)
    # Steady runtime metrics around 25°C mixed with sudden extreme error spikes (e.g., 95.0, -12.0)
    factory_temperature_log = [24.5, 25.2, 24.8, 95.0, 25.1, 24.9, -12.0, 25.5, 24.7]
    
    filter_sensor_stream(factory_temperature_log, z_threshold=1.8)