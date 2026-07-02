# Implementing algebraic Euclidean distance functions for ML geometric models

import numpy as np

def calculate_euclidean_distance(vector_a, vector_b):
    """
    Computes the mathematical Euclidean distance between two multi-dimensional arrays.
    Formula: d = sqrt(sum((x_i - y_i)^2))
    """
    print("---  AI Matrix Geometry: Euclidean Distance Engine ---")
    
    # 1. Cast inputs into standard NumPy arrays to ensure matrix operations support
    arr_a = np.array(vector_a, dtype=float)
    arr_b = np.array(vector_b, dtype=float)
    
    print(f"Vector Alpha Coordinate Profile : {arr_a}")
    print(f"Vector Beta Coordinate Profile  : {arr_b}\n")
    
    # 2. Linear Algebra Vector Arithmetic Steps
    # Step A: Find vector differences (displacement)
    displacement = arr_a - arr_b
    
    # Step B: Compute sum of squared errors
    squared_displacement = np.square(displacement)
    sum_of_squares = np.sum(squared_displacement)
    
    # Step C: Take the square root to finalize the dimensional distance
    distance = np.sqrt(sum_of_squares)
    
    print(f" Matrix Evaluation Report:")
    print(f"  Vector Displacement Delta: {np.round(displacement, 2)}")
    print(f"  Resulting Absolute Euclidean Distance: {distance:.4f}")
    
    return distance

if __name__ == "__main__":
    # Simulated 3D feature arrays representing two data items
    # Example: [Age, Skill Keywords Profile Match %, System Activity Score]
    feature_profile_1 = [19.0, 85.5, 92.0]
    feature_profile_2 = [23.0, 70.0, 45.0]
    
    calculate_euclidean_distance(feature_profile_1, feature_profile_2)