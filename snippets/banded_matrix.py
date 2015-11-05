import numpy as np
from scipy.linalg import solve_banded

from sympy import pprint, Symbol, lambdify

A = np.array([
    [20, -5, 0, 0],
    [-5, 15, -5, 0],
    [0, -5, 15, -5],
    [0, 0, -5, 10]
], dtype=np.float)

D = np.array([1100, 100, 100, 100], dtype=np.float)

# upper diagonal
ud = np.insert(np.diag(A, 1), 0, 0)
# main diagonal
d = np.diag(A)
# lower diagonal
ld = np.insert(np.diag(A, -1), len(d) - 1, 0)

print ud
print d
print ld

# simplified matrix
ab = np.matrix([
    ud,
    d,
    ld
])

