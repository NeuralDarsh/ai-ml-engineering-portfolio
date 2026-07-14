# Implementing algebraic data dispersion algorithms to screen low-variance ML features

import numpy as np

def calculate_feature_variance(data_stream):
    """
    Computes the mathematical variance of a multi-dimensional data vector.
    Formula: Variance = sum((x_i - mean)^2) / N
    Identifies if the array falls below standard low-variance information thresholds.
    """
    print("--- Machine Learning Core Math: Feature Variance Engine ---")
    
    # 1. Cast input into a formal NumPy 1D vector array
    vec = np.array(data_stream, dtype=float)
    total_elements = len(vec)
    
    print(f"Ingested Feature Vector : {vec}")
    print(f"Total Sample Space Size : {total_elements} entries\n")
    
    # 2. Step-by-step linear algebra deviation steps
    mean_val = np.mean(vec)
    
    # Calculate difference between each element and the vector mean
    deviations = vec - mean_val
    
    # Square the deviations to eliminate negative signs
    squared_deviations = np.square(deviations)
    
    # Average the squared values to calculate the final statistical variance
    variance_score = np.sum(squared_deviations) / total_elements
    
    print(" Statistical Processing Log:")
    print(f"  Calculated Feature Mean : {mean_val:.3f}")
    print(f"  Inherent System Variance : {variance_score:.4f}")
    
    # 3. Enterprise Feature Selection Threshold Rule (Limit set to 0.01)
    # If values fluctuate less than 0.01, the feature is discarded as noise
    THRESHOLD = 0.01
    
    if variance_score < THRESHOLD:
        return " REJECT: Low-variance feature detected. Discard array from ML training matrix."
    else:
        return "ACCEPT: Feature dispersion is healthy. Retain array for model training pipelines."

if __name__ == "__main__":
    # Case A: Simulated dynamic IoT sensor input stream (Healthy Variance)
    dynamic_signal = [24.5, 28.2, 22.1, 31.4, 25.8]
    verdict_A = calculate_feature_variance(dynamic_signal)
    print(f"Feature Router Status: {verdict_A}")
    
    print("\n" + "="*60 + "\n")
    
    # Case B: Simulated flat, redundant baseline stream (Low Variance)
    flat_signal = [12.00, 12.01, 11.99, 12.00, 12.00]
    verdict_B = calculate_feature_variance(flat_signal)
    print(f"Feature Router Status: {verdict_B}")