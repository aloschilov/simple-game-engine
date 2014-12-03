from force import Force

import numpy as np

from math import sqrt


def find_nearest_element_index(array, value):
    idx = (np.abs(array-value)).argmin()
    return idx


class RadialForce(Force):
    """
    This class stands for method of force specification,
    where we specify potential function on 2D space
    by specifying relation between force potential and distance
    to a point in concern from center of the matter.
    """

    def __init__(self):
        self.bezier_curve_points = None

    def set_bezier_curve(self,
                         control_points,
                         points_per_segment=10000):
        """

        :param control_points:
        :return:
        """

        number_of_points = len(control_points)/2
        number_of_segments = int(number_of_points/3)
        numpy_points = np.array(control_points)
        numpy_points = numpy_points.reshape((number_of_points, 2))

        gamma_0 = 3
        gamma_1 = 3

        b_0 = lambda t: 1 - gamma_0*t + (2*gamma_0 - 3)*t**2 + (2 - gamma_0)*t**3
        b_1 = lambda t: gamma_0*t*(1-t)**2
        b_2 = lambda t: gamma_1*t**2*(1-t)
        b_3 = lambda t: (3-gamma_1)*t**2 + (gamma_1-2)*t**3

        p = lambda u_0, v_0, v_1, u_1, t: b_0(t)*u_0 + b_1(t)*v_0 + b_2(t)*v_1 + b_3(t)*u_1

        bezier_curve_points = np.empty((0, 2))

        for i in xrange(number_of_segments):
            u_0 = numpy_points[0+i*3, :]
            v_0 = numpy_points[1+i*3, :]
            v_1 = numpy_points[2+i*3, :]
            u_1 = numpy_points[3+i*3, :]
            p_current = np.frompyfunc(lambda t: p(u_0, v_0, v_1, u_1, t), 1, 1)
            segment_points = np.vstack(p_current(np.linspace(0, 1, points_per_segment)))
            segment_points.reshape((points_per_segment, 2))
            bezier_curve_points = np.concatenate((bezier_curve_points, segment_points))

        self.bezier_curve_points = bezier_curve_points

    def function(self):
        """

        :return:
        """

        def cartesian_function(point):
            x, y = (point[0]/10.0, point[1]/10.0)
            rho = sqrt(x*x+y*y)
            h_idx = find_nearest_element_index(self.bezier_curve_points[:, 0], rho)
            h = self.bezier_curve_points[h_idx, 1]
            return h*10

        return cartesian_function

