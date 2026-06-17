# Implementing core Linear Algebra data transformation pipelines using NumPy

import numpy as np

def scale_features(data_matrix):
    """
    Applies Min-Max Normalization to scale matrix columns between 0 and 1.
    Formula: X_scaled = (X - X_min) / (X_max - X_min)
    """
    print("---  AI Feature Scaling Pipeline (線形代数スケーリング) ---")
    print(f"Original Data Matrix:\n{data_matrix}\n")
    
    # 1. Find the minimum and maximum values along the column axis (axis=0)
    col_min = np.min(data_matrix, axis=0)
    col_max = np.max(data_matrix, axis=0)
    
    # 2. Prevent division-by-zero errors using a fallback guardrail
    denominator = col_max - col_min
    denominator[denominator == 0] = 1.0
    
    # 3. Apply the Linear Algebra scaling matrix transformation
    scaled_matrix = (data_matrix - col_min) / denominator
    
    print(f"Scaled Matrix (Values Bound between 0 and 1):\n{np.round(scaled_matrix, 3)}")
    return scaled_matrix

if __name__ == "__main__":
    # Simulated ML dataset matrix: Rows = Samples, Columns = [Feature 1, Feature 2]
    # Example: Column 1 could be room temperature, Column 2 could be network ping
    raw_dataset = np.array([
        [10.0, 500.0],
        [20.0, 1500.0],
        [30.0, 2500.0],
        [40.0, 3500.0]
    ])
    
    scale_features(raw_dataset)