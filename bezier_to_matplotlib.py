import numpy as np
import matplotlib.pyplot as plt

original_points = [0, 0, 0.4, 0.075, 0.462, 0.252, 0.512, 0.512, 0.562, 0.772, 0.7, 0.9, 1, 1]
number_of_points = len(original_points)/2
number_of_segments = int(number_of_points/3)
numpy_points = np.array(original_points)
numpy_points = numpy_points.reshape((number_of_points, 2))

print "number_of_points = {nop}".format(nop=number_of_points)
print "number_of_segments = {nos}".format(nos=number_of_segments)

xs = numpy_points[:, 0]
ys = numpy_points[:, 1]

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
    segment_points = np.vstack(p_current(np.linspace(0, 1, 100)))
    segment_points.reshape((100, 2))
    bezier_curve_points = np.concatenate((bezier_curve_points, segment_points))

plt.plot(xs, ys, "ro")
plt.plot(bezier_curve_points[:, 0], bezier_curve_points[:, 1])
plt.show()
