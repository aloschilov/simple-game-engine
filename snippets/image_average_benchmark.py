def test():
    """Stupid test function"""
    L = []
    for i in range(100):
        L.append(i)

if __name__ == '__main__':
    import timeit

    setup = """
import numpy as np
from engine.interpolate import splint2
from sympy.plotting import plot3d
from sympy.abc import x, y
from scipy import misc

image = misc.imread('bitmap_force_input.jpg')
image = image.astype(dtype=np.float)

def average(pixel):
    return (pixel[0] + pixel[1] + pixel[2]) / 3

grey = np.zeros((image.shape[0], image.shape[1]), dtype=np.float) # init 2D numpy array
    """

    print(timeit.timeit("""

for rownum in range(len(image)):
   for colnum in range(len(image[rownum])):
      grey[rownum][colnum] = average(image[rownum][colnum])
      """
                        , setup=setup, number=1000))
    print (timeit.timeit("""
grey = np.add.reduce(image, 2)/3.0
    """, setup=setup, number=1000))
