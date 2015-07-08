def atoms_quantities_to_image(name_and_quantity_list, matter_name):
    """

    :param name_and_quantity_list: list of pairs (name, quantity)
    where name stands for Atom name and quantity stands for number of
    atoms in specific matter
    :return: ndarray with shape (width, height, 4) and dtype=uint8
    """

    from matplotlib.figure import Figure
    from numpy import arange, frombuffer, uint8
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

    if name_and_quantity_list:
        names, quantities = zip(*name_and_quantity_list)
        pos = arange(len(names))
    else:
        names = []
        quantities = []
        pos = arange(len(names))

    figure = Figure()
    figure.patch.set_facecolor('none')
    figure.patch.set_alpha(0.0)
    figure.set_size_inches(5, 5)
    axes = figure.add_subplot(111)
    axes.barh(pos, quantities, align='center', alpha=0.4)
    axes.yaxis.set_ticks(pos)
    axes.yaxis.set_ticklabels(names)
    axes.set_xlabel('Quantity')
    axes.set_title(matter_name)
    axes.patch.set_visible(False)

    canvas = FigureCanvas(figure)
    data, shape = canvas.print_to_buffer()
    y, x = shape

    array = frombuffer(data, dtype=uint8, count=x*y*4)
    return array.reshape((x, y, 4))
