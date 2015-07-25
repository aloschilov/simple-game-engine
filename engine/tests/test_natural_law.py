def test_get_matrix_of_converted_atoms():
    from sympy import symbols, Matrix, Piecewise, sqrt
    from engine.natural_law import get_matrix_of_converted_atoms
    from numpy import array

    x, y = symbols('x y')

    Nu = Matrix([[1.0, 0.0, 101.0]])
    ps = [array([0., 0.])]
    pending_transformation_vector = Matrix([[0], [9.0 * Piecewise((1.0,
                                                                   0.204 * (x ** 2 + y ** 2) ** (3 / 2) + 91.8 * sqrt(
                                                                       x ** 2 + y ** 2) * (
                                                                       -sqrt(x ** 2 + y ** 2) / 10 + 1) ** 2 + 3.06 * (
                                                                       x ** 2 + y ** 2) * (
                                                                       -0.3 * sqrt(x ** 2 + y ** 2) + 3.0) + 306.0 * (
                                                                       -sqrt(x ** 2 + y ** 2) / 10 + 1) ** 3 > 0.0),
                                                                  (0.0,
                                                                   0.204 * (
                                                                       x ** 2 + y ** 2) ** (
                                                                       3 / 2) + 91.8 * sqrt(
                                                                       x ** 2 + y ** 2) * (
                                                                       -sqrt(
                                                                           x ** 2 + y ** 2) / 10 + 1) ** 2 + 3.06 * (
                                                                       x ** 2 + y ** 2) * (
                                                                       -0.3 * sqrt(
                                                                           x ** 2 + y ** 2) + 3.0) + 306.0 * (
                                                                       -sqrt(
                                                                           x ** 2 + y ** 2) / 10 + 1) ** 3 <= 0.0))],
                                            [0]])

    natural_influence = Matrix([[9.0 * Piecewise((1.00000000000000, 0.204 * (x ** 2 + y ** 2) ** (3 / 2) + 91.8 * sqrt(
        x ** 2 + y ** 2) * (-sqrt(x ** 2 + y ** 2) / 10 + 1) ** 2 + 3.06 * (x ** 2 + y ** 2) * (
                                                      -0.3 * sqrt(x ** 2 + y ** 2) + 3.0) + 306.0 * (
                                                      -sqrt(x ** 2 + y ** 2) / 10 + 1) ** 3 > 0.0), (0.0, 0.204 * (
        x ** 2 + y ** 2) ** (3 / 2) + 91.8 * sqrt(x ** 2 + y ** 2) * (-sqrt(x ** 2 + y ** 2) / 10 + 1) ** 2 + 3.06 * (
                                                                                                         x ** 2 + y ** 2) * (
                                                                                                         -0.3 * sqrt(
                                                                                                             x ** 2 + y ** 2) + 3.0) + 306.0 * (
                                                                                                         -sqrt(
                                                                                                             x ** 2 + y ** 2) / 10 + 1) ** 3 <= 0.0))]])
    Omicron = Matrix([[0, 1, 0]])
    D = Matrix([[0, 0, 1]])

    assert get_matrix_of_converted_atoms(Nu, ps, pending_transformation_vector, natural_influence, Omicron, D) == Matrix([[0.0, 0.0, 0.0]])


