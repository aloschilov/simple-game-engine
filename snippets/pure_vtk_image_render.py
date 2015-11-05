import numpy
from vtk.util import numpy_support
from scipy.misc import lena
import vtk

l = lena()
vtk_data_array = numpy_support.numpy_to_vtk(l.flatten()) #transpose(1,0).

image = vtk.vtkImageData()
#image.SetNumberOfScalarComponents(2)
#image.SetScalarType(VTK_UNSIGNED_CHAR)
#   output->SetNumberOfScalarComponents(3);
image.SetDimensions(l.shape + (1,))
points = image.GetPointData()
points.SetScalars(vtk_data_array)
image.Update()

image_actor = vtk.vtkImageActor()
image_actor.GetMapper().SetInput(image)
render = vtk.vtkRenderer()
render.AddActor( image_actor )
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer( render )
renderWindow.SetSize( 300, 300)
render_window_interactor = vtk.vtkRenderWindowInteractor()
render_window_interactor.SetRenderWindow(renderWindow)
render_window_interactor.Start()

# Initialize and start the event loop.
render_window_interactor.Initialize()
renderWindow.Render()
render_window_interactor.Start()
