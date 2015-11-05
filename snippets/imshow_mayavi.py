from mayavi import mlab
import pylab as pl
from numpy import frombuffer, uint8


def simple():
    import datetime
    import random

    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.dates import DateFormatter

    fig = Figure()
    ax = fig.add_subplot(111)
    x = []
    y = []
    now = datetime.datetime.now()
    delta = datetime.timedelta(days=1)
    for i in range(10):
        x.append(now)
        now += delta
        y.append(random.randint(0, 1000))
    ax.plot_date(x, y, '-')
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()

    canvas = FigureCanvas(fig)
    data, shape = canvas.print_to_buffer()
    y, x = shape

    array = frombuffer(data, dtype=uint8, count=x*y*4)
    return array.reshape((x, y, 4))

def mlab_imshowColor(im, alpha=255, **kwargs):
    """
    Plot a color image with mayavi.mlab.imshow.
    im is a ndarray with dim (n, m, 3) and scale (0->255]
    alpha is a single number or a ndarray with dim (n*m) and scale (0->255]
    **kwargs is passed onto mayavi.mlab.imshow(..., **kwargs)
    """
    try:
        alpha[0]
    except:
        alpha = pl.ones(im.shape[0] * im.shape[1]) * alpha
    if len(alpha.shape) != 1:
        alpha = alpha.flatten()

    # The lut is a Nx4 array, with the columns representing RGBA
    # (red, green, blue, alpha) coded with integers going from 0 to 255,
    # we create it by stacking all the pixles (r,g,b,alpha) as rows.
    myLut = pl.c_[im.reshape(-1, 3), alpha]
    myLutLookupArray = pl.arange(im.shape[0] * im.shape[1]).reshape(im.shape[0], im.shape[1])

    #We can display an color image by using mlab.imshow, a lut color list and a lut lookup table.
    theImshow = mlab.imshow(myLutLookupArray, colormap='binary', **kwargs) #temporary colormap
    theImshow.module_manager.scalar_lut_manager.lut.table = myLut
    mlab.draw()

    return theImshow


if __name__ == '__main__':
    im = simple()
    mlab_imshowColor(im[:, :, :3], im[:, :, -1])
    mlab.show()
