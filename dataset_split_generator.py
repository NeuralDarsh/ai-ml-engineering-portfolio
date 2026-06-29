# Implementing deterministic random array slicing pipelines for ML preprocessing models

import numpy as np

def generate_train_test_indices(total_samples, train_ratio=0.8, seed=42):
    """
    Shuffles indices deterministically and splits them into training and testing arrays.
    Prevents data leakage by generating consistent index splits using fixed math seeds.
    """
    print("---  AI Preprocessing: Dataset Train-Test Split Engine ---")
    print(f"Total Samples Detected: {total_samples} entries")
    
    # 1. Initialize a deterministic random state sequence (Seed 42)
    rng = np.random.default_rng(seed)
    
    # 2. Generate a linear array of indices and shuffle them
    indices = np.arange(total_samples)
    rng.shuffle(indices)
    
    # 3. Calculate mathematical split boundary threshold
    split_boundary = int(total_samples * train_ratio)
    
    # 4. Matrix array slicing logic
    train_indices = indices[:split_boundary]
    test_indices = indices[split_boundary:]
    
    print(f"Split Framework Profile (Ratio: {train_ratio*100:.0f}% / {(1-train_ratio)*100:.0f}%)")
    print(f"  Training Data Allocation Size: {len(train_indices)} entries")
    print(f"  Testing Data Allocation Size:  {len(test_indices)} entries\n")
    
    print(f"Sample Shuffled Training Indices: {train_indices[:5]}...")
    print(f"Sample Shuffled Testing Indices:  {test_indices[:5]}...")
    
    return train_indices, test_indices

if __name__ == "__main__":
    # Simulated enterprise database table containing 120 dataset feature vectors
    simulated_row_count = 120
    
    generate_train_test_indices(total_samples=simulated_row_count, train_ratio=0.8)