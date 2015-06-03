from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput

from IPython.display import Image # optional for ipython

def test2(i):
    return i*i

def test3(f):
    return f**1.1

def test(n):
    total = 0
    for i in range(n):
        total += test2(n)/test3(n)
    return total

with PyCallGraph(output=GraphvizOutput()):
    test(1111)
    
Image("pycallgraph.png") #if not in ipython search this image manually