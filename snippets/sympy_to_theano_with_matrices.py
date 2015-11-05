from sympy import MatrixSymbol, Matrix, pprint, HadamardProduct
from sympy.abc import x, y
from sympy.printing import ccode

M = 3
A = 4

Nu = MatrixSymbol('Nu', M, A)
p = MatrixSymbol('p', M, 2)

G = Matrix([[1, 0, 0, 1, 1, 0],
            [0, 0, 0, 1, 0, 0],
            [0, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 1]])

fs = [x*1+10,
      x*2+10,
      x*3+10,
      x*4+10,
      x*5+10,
      x*6+10]

F = Matrix(M, len(fs), lambda i, j: fs[j].subs({x: x-p[i, 0], y: y-p[i, 1]}))

P = Matrix([[Matrix(1, M, lambda i, j: 0 if j == k else 1)*(HadamardProduct(Nu*G, F))
     for k in xrange(0, M)]])

pprint(P, num_columns=500)

inputs = [x, y, p]
outputs = [P]
dtypes = {inp: 'float64' for inp in inputs}

#from sympy.printing.theanocode import theano_function
#f = theano_function(inputs, outputs)
S = MatrixSymbol('C', 1, M)

print ccode(P, S)
