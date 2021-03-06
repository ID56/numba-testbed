import numpy as np
import numba as nb
from timeit import timeit
from scipy.ndimage.morphology import binary_dilation


@nb.njit(cache=True, fastmath=True)
def njit_dilateB(a, b, c, i0, i1, j0, j1):
    """Looped binary dilation."""

    for i in range(i0, i1):
        for j in range(j0, j1):

            for k in range(b.shape[0]):
                for l in range(b.shape[1]):
                    if b[k, l] and a[i+k-i0, j+l-j0]:
                        c[i-i0, j-j0] = True 
                        break
                
                if c[i-i0, j-j0]: 
                    break
                    
    return c


def dilateWrapper(a, b):
    """Wrapper for njit_dilateB."""
    px, py = b.shape
    px, py = px//2, py//2

    a_ = np.pad(a, (px,py), constant_values=(0,0))
    b = np.flip(b)
    c = np.zeros_like(a)
    
    c = njit_dilateB(a_, b, c, px, a_.shape[0]-px, py, a_.shape[1]-py)
    return c


def test_equality(N, M):
    print(f'Testing equality with {N}x{N} input and {M}x{M} kernel...')
    a = np.random.choice(2, (N, N)).astype(bool)
    b = np.random.choice(2, (M, M)).astype(bool)

    out = binary_dilation(a, b)
    out_l = dilateWrapper(a, b)


    print('Equality with NJIT loop:', np.array_equal(out, out_l))

def test_runtime(N, M):
    print(f'Testing runtime with {N}x{N} input and {M}x{M} kernel...')
    a = np.random.choice(2, (N, N)).astype(bool)
    b = np.random.choice(2, (M, M)).astype(bool)

    nl = 1
    print('Scipy binary dilation:', timeit(lambda: binary_dilation(a, b), number=nl))
    print('NJIT compiled kernel: ', timeit(lambda: dilateWrapper(a, b), number=nl))
    # roughly 1.5x gain


if __name__ == '__main__':
    N = 1000
    M = 3

    assert M % 2 == 1, 'Use odd kernel size.'

    test_equality(N, M)
    test_runtime(N, M)