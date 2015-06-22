def vector_field_to_image(vector_field_and_color, rect):
    """
    :param vector_field:
    :return: ndarray with shape (width, height, 4) and dtype=uint8
    """

    vector_field, color = vector_field_and_color

    from sympy import lambdify, symbols
    from numpy import mgrid, frombuffer, uint8, vectorize
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

    x, y = symbols("x y")

    u = vectorize(lambdify((x, y),
                           vector_field[0],
                           "numpy"))

    v = vectorize(lambdify((x, y),
                           vector_field[1],
                           "numpy"))

    left, top, right, bottom = rect

    y, x = mgrid[bottom:top:100j, left:right:100j]
    U, V = (u(x, y), v(x, y))

    figure = Figure(frameon=False)
    figure.patch.set_facecolor('none')
    figure.patch.set_alpha(0.0)
    figure.set_size_inches(10, 10)
    figure.patch.set_visible(False)
    figure.subplots_adjust(left=0, right=1, top=1, bottom=0)
    axes = figure.add_subplot(111)
    axes.streamplot(x, y, U, V, color=color)
    axes.axis('off')
    axes.patch.set_visible(False)

    canvas = FigureCanvas(figure)
    data, shape = canvas.print_to_buffer()

    y, x = shape

    array = frombuffer(data, dtype=uint8, count=x*y*4)
    return array.reshape((x, y, 4))
