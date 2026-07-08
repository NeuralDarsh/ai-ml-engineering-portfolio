# Implementing mathematical vector normalizations using NumPy broadcast divisions

import numpy as np

def scale_vector_coordinates(raw_vector, scale_min=0.0, scale_max=1.0):
    """
    Normalizes an independent vector array into user-defined bounding limits.
    Formula: X_scaled = scale_min + ((X - X_min) * (scale_max - scale_min)) / (X_max - X_min)
    """
    print("--- Machine Learning Preprocessing: Vector Min-Max Scaler ---")
    
    # 1. Cast input to standard NumPy float vector array
    vec = np.array(raw_vector, dtype=float)
    print(f"Raw Input Vector Array  : {vec}")
    print(f"Target Normalization Bounds: [{scale_min}, {scale_max}]\n")
    
    # 2. Extract bounding limits
    v_min = np.min(vec)
    v_max = np.max(vec)
    
    # 3. Mathematical Zero-Variance Guardrail
    # Prevents crashing with a division-by-zero error if all elements in the vector are identical
    denominator = v_max - v_min
    if denominator == 0.0:
        print("  ZERO VARIANCE DETECTED: Vector components are uniform. Returning base limits matrix.")
        return np.full_like(vec, scale_min)
        
    # 4. Perform element-wise algebraic scaling transformation
    normalized_vector = scale_min + ((vec - v_min) * (scale_max - scale_min)) / denominator
    
    print(" Scaling Matrix Operations Log:")
    print(f"  Extracted Vector Extremes : Min={v_min}, Max={v_max}")
    print(f"  Transformed Vector Output : {np.round(normalized_vector, 4)}")
    return normalized_vector

if __name__ == "__main__":
    # Simulated 1D image pixel feature array intensity values (0 to 255 baseline)
    # Squeezing raw camera sensors data down into a standard [0, 1] neural network input range
    simulated_pixel_row = [12.0, 45.5, 255.0, 128.0, 0.0, 88.3]
    
    scale_vector_coordinates(simulated_pixel_row, scale_min=0.0, scale_max=1.0)