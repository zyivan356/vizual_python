# cython: language_level=3
import numpy as np
from cython.parallel import prange

# Автоматически компилируется в C++ с оптимизациями
def calculate_stress(double[:, :] strain_tensor, double young_modulus):
    """
    Расчёт тензора напряжений по закону Гука (3D).
    Выполняется на C++ после компиляции.
    """
    cdef int i, j
    cdef int n = strain_tensor.shape[0]
    cdef double[:, :] stress_tensor = np.zeros((n, 3))

    # Параллельный цикл через OpenMP
    for i in prange(n, nogil=True):
        stress_tensor[i, 0] = young_modulus * strain_tensor[i, 0]  # σ_x
        stress_tensor[i, 1] = young_modulus * strain_tensor[i, 1]  # σ_y
        stress_tensor[i, 2] = young_modulus * strain_tensor[i, 2]  # σ_z

    return np.asarray(stress_tensor)