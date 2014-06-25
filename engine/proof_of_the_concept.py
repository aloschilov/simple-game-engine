import os
os.environ['ETS_TOOLKIT'] = 'qt4'

from mayavi import mlab

from tvtk.api import tvtk

import numpy

v = mlab.figure()
sphere = tvtk.SphereSource(center=(0, 0, 0), radius=0.5)
sphere_mapper = tvtk.PolyDataMapper(input=sphere.output)
p = tvtk.Property(opacity=1, color=(1,0,0))
sphere_actor = tvtk.Actor(mapper=sphere_mapper, property=p)
v.scene.add_actor(sphere_actor)

def f(x, y):
    array_to_return = 1.0/(x*x + y*y)
    shape_to_update = array_to_return[(x*x+y*y)<0.5].shape
    array_to_return[(x*x+y*y)<0.5] = numpy.ones(shape_to_update)*2
    return array_to_return


x, y = numpy.mgrid[-7.:7.00:100j, -5.:5.00:100j]
s = mlab.surf(x, y, f)

# Choose a view angle, and display the figure
mlab.view(85, -17, 15, [3.5, -0.3, -0.8])
mlab.show()