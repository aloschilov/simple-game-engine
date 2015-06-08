def vector_field_to_image(vector_field, R, rect):
    """
    :param vector_field:
    :return: ndarray with shape (width, height, 4) and dtype=uint8
    """

    from sympy import lambdify
    from numpy import mgrid, frombuffer, uint8, vectorize
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

    u = vectorize(lambdify((R[0], R[1]),
                           vector_field.to_matrix(R)[0],
                           "numpy"))

    v = vectorize(lambdify((R[0], R[1]),
                           vector_field.to_matrix(R)[1],
                           "numpy"))

    left, top, right, bottom = rect

    y, x = mgrid[bottom:top:100j, left:right:100j]
    U, V = (u(x, y), v(x, y))

    figure = Figure()
    figure.patch.set_facecolor('none')
    figure.patch.set_alpha(0.0)
    axes = figure.add_subplot(111)
    axes.streamplot(x, y, U, V)
    axes.axis('off')

    canvas = FigureCanvas(figure)
    data, shape = canvas.print_to_buffer()
    y, x = shape

    array = frombuffer(data, dtype=uint8, count=x*y*4)
    return array.reshape((x, y, 4))
