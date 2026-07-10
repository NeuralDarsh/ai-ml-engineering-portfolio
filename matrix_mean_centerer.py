# Implementing matrix axis reductions and row broadcasts to center ML feature arrays

import numpy as np

def mean_center_dataset(data_matrix):
    """
    Computes column means and subtracts them from each row vector in the matrix.
    Shifts the feature space coordinate center directly to the mathematical origin (0).
    """
    print("---  AI Preprocessing Pipeline: Matrix Mean-Centering ---")
    
    # 1. Cast input into a formal NumPy 2D float array matrix
    matrix = np.array(data_matrix, dtype=float)
    print(f"Original Feature Matrix:\n{matrix}\n")
    
    # 2. Compute the mean values along the vertical column axis (axis=0)
    column_means = np.mean(matrix, axis=0)
    print(f"Calculated Baseline Column Means: {np.round(column_means, 3)}\n")
    
    # 3. Apply element-wise row subtraction via NumPy Matrix Broadcasting
    centered_matrix = matrix - column_means
    
    # 4. Verify the math by computing the fresh centered column means (should be ~0.0)
    verified_means = np.mean(centered_matrix, axis=0)
    
    print(" Transformation Matrix Execution Verdict:")
    print(f"   Mean-Centered Matrix Layout:\n{np.round(centered_matrix, 3)}")
    print(f"   Verification Phase: New Column Means are mathematically zero: {np.allclose(verified_means, 0.0)}")
    
    return centered_matrix

if __name__ == "__main__":
    # Simulated 4x3 dataset array profile
    # Rows = 4 distinct data samples, Columns = [Feature 1, Feature 2, Feature 3]
    # Example columns could map to sensor metrics, keyword counts, or network latency parameters
    simulated_dataset = [
        [10.0, 200.0, 1.5],
        [40.0, 100.0, 3.5],
        [20.0, 600.0, 2.0],
        [50.0, 300.0, 5.0]
    ]
    
    mean_center_dataset(simulated_dataset)