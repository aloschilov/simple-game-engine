import os

from sympy import symbols
import pickle

if __name__ == "__main__":

    x, y = symbols("x y")
    expr = x**2 + y**2

    output_file = open("mydata.dat", "w")
    p = pickle.Pickler(output_file)
    p.dump(expr)
    output_file.close()
