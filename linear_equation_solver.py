# Utilizing NumPy's algebraic matrix engine to solve simultaneous equations safely

import numpy as np

def solve_linear_system(matrix_A, vector_b):
    """
    Solves the linear matrix equation Ax = b for unknown vector x.
    Includes algebraic exception testing to catch non-invertible/singular matrices.
    """
    print("---  Linear Algebra: Simultaneous Equation Solver ---")
    
    A = np.array(matrix_A, dtype=float)
    b = np.array(vector_b, dtype=float)
    
    print(f"Matrix A (Coefficients):\n{A}")
    print(f"Vector b (Constants):\n{b}\n")
    
    try:
        # 1. Check determinant to verify matrix invertibility and prevent crashes
        det = np.linalg.det(A)
        if np.isclose(det, 0.0):
            raise np.linalg.LinAlgError("Matrix A is singular (Determinant is 0). System cannot be solved.")
            
        # 2. Compute the unknown vector weights using optimized algebra wrappers
        solution_x = np.linalg.solve(A, b)
        
        print(" Algebraic Execution Verdict:")
        print(f"   System Solved Safely (Determinant: {det:.2f})")
        print(f"   Vector Solution x (Weights Matrix): {np.round(solution_x, 4)}")
        return solution_x
        
    except np.linalg.LinAlgError as error:
        print(f"   PRODUCTION ERROR ACCESSED: {error}")
        return None

if __name__ == "__main__":
    # Simulate a system of linear equations:
    # 2x + 3y = 8
    # 1x - 2y = -3
    simulated_coefficients = [[2, 3], [1, -2]]
    simulated_constants = [8, -3]
    
    solve_linear_system(simulated_coefficients, simulated_constants)