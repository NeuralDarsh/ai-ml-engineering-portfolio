# Implementing vector-based window transformations to clean noisy ML input signals

import numpy as np

def denoise_signal(noisy_vector, window_size=3):
    """
    Applies a mathematical 1D moving average filter over a data stream vector.
    Smooths high-frequency fluctuations to optimize downstream AI model inference.
    """
    print("--- AI Pipeline: Data Stream Signal Denoiser ---")
    print(f"Raw Input Vector (Size {len(noisy_vector)}):\n{noisy_vector}\n")
    
    # 1. Allocate an empty structure matching our target output scale
    smoothed_vector = np.copy(noisy_vector)
    
    # 2. Vector window slice allocation logic
    # Computes average for middle components bounded by boundary frames
    for i in range(1, len(noisy_vector) - 1):
        # Slice out a rolling localized window cluster around element i
        window = noisy_vector[i - 1 : i + 2]
        smoothed_vector[i] = np.mean(window)
        
    print(f"Denoised Output Vector (Smoothed Matrix):\n{np.round(smoothed_vector, 2)}")
    return smoothed_vector

if __name__ == "__main__":
    # Simulated continuous IoT sensor reading vector stream
    # Contains minor baseline fluctuations mixed with harsh spike noise errors (e.g., 85.0)
    raw_signal = np.array([22.1, 22.4, 21.9, 85.0, 23.2, 22.8, 22.5, 79.5, 22.2])
    
    denoise_signal(raw_signal, window_size=3)