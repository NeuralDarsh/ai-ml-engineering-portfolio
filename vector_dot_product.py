# Implementing algebraic vector multiplication kernels for neural network weights

import numpy as np

def compute_feature_alignment(vector_features, vector_weights):
    """
    Computes the mathematical dot product of two multi-dimensional arrays.
    Formula: dot_product = sum(x_i * y_i)
    Validates array dimensions to guarantee safe algebraic execution.
    """
    print("---  Linear Algebra Engine: Vector Dot Product ---")
    
    # 1. Cast inputs to formal NumPy structure arrays
    v_f = np.array(vector_features, dtype=float)
    v_w = np.array(vector_weights, dtype=float)
    
    # 2. Structural Dimension Gatekeeper
    if v_f.shape != v_w.shape:
        print(f"  MATRIX SHAPE ERROR: Dimension mismatch {v_f.shape} vs {v_w.shape}!")
        return None
        
    print(f"Feature Vector Ingest : {v_f}")
    print(f"Weight Tensor Ingest  : {v_w}\n")
    
    # 3. Perform the algebraic dot product transformation
    # Using NumPy's highly optimized native .dot() function
    alignment_score = np.dot(v_f, v_w)
    
    print(" Core Multiplication Matrix Verdict:")
    print(f"   Matrix Sizes Match: {v_f.shape}")
    print(f"   Computed Scalar Dot Product Score: {alignment_score:.4f}")
    return alignment_score

if __name__ == "__main__":
    # Simulated 4-dimensional data arrays
    # Example: Matching a candidate profile vector against an engineering job weight vector
    # Matrix columns map to: [Python Skill, ML Foundations, IoT Knowledge, JLPT Japanese Level]
    candidate_profile_features = [0.90, 0.85, 0.70, 0.40] 
    job_requirement_weights   = [10.0,  12.0,   5.0,   8.0]
    
    compute_feature_alignment(candidate_profile_features, job_requirement_weights)