import numpy as np
import numba as nb
from timeit import timeit
from scipy.ndimage.morphology import binary_dilation


@nb.stencil(standard_indexing=("b",), neighborhood = ((-1, 1),(-1,1)))
def _stcl_kernel(a, b):
    """Stencil kernel for 3x3 binary dilation."""

    for i in range(-1, 2):
        for j in range(-1, 2):
            if a[i,j] and b[i+1,j+1]:
                return True
    return False

@nb.njit(parallel=True, cache=True, fastmath=True)
def dilate3x3(a, b):
    """JIT wrapper for _stcl_kernel."""
    return _stcl_kernel(a,b)


def test_equality(N):
    print(f'Testing equality with {N}x{N} array.')
    a = np.zeros((N,N), dtype=bool)
    np.random.seed(0)
    a[tuple(np.random.choice(N,N//2)), tuple(np.random.choice(N,N//2))] = 1
    b = np.array([[0, 1, 0],
                  [1, 0, 1],
                  [0, 1, 0]], dtype = bool)
    
    # padding is needed to handle border values
    p = 1
    a_ = np.pad(a, (p,p), constant_values=(0,0))
    out = dilate3x3(a_, b)[p:-p,p:-p]
    out_ = binary_dilation(a, b)
    print('Equality:', np.array_equal(out, out_))


def test_runtime(N):
    print(f'Testing runtime with {N}x{N} array.')
    a = np.zeros((N,N), dtype=bool)
    np.random.seed(56)
    a[tuple(np.random.choice(N,N//2)), tuple(np.random.choice(N,N//2))] = 1

    b = np.array([[0, 1, 0],
                  [1, 0, 1],
                  [0, 1, 0]], dtype = bool)
    
    # padding is needed to handle border values
    p = 1
    a_ = np.pad(a, (p,p), constant_values=(0,0))

    nl = 10
    print('Scipy binary dilation:', timeit(lambda: binary_dilation(a, b), number=nl))
    print('JIT compiled stencil: ', timeit(lambda: dilate3x3(a_, b), number=nl))
    # roughly 2x gain
    
if __name__ == '__main__':
    N = 1000
    test_equality(N)
    test_runtime(N)
