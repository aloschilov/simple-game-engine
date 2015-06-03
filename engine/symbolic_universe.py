from traits.api import HasTraits, Instance, List, on_trait_change
from sympy import Matrix, init_printing, pprint, Piecewise, symbols, And, lambdify, diag, ones, diff
from numpy import vectorize, array
from mayavi.core.ui.api import MlabSceneModel

from . import Matter, Atom, Force, RadialForce



class Universe(HasTraits):
    """
    A hypothetical universe, where in its 2d Space, Forces
    control what happen. There is Matter build out of different
    Atoms able to move. Each Atom affect the Forces.
    The NaturalLaws define how Atoms convert into other Atoms,
    if certain Forces are present.
    """

    atoms = List(trait=Instance(Atom))
    forces = List(trait=Instance(Force))
    matters = List(trait=Instance(Matter))
    scene = Instance(MlabSceneModel, ())

    def create_matter(self):
        """

        """

        matter = Matter()
        self.matters.append(matter)
        self.scene.add_actor(matter.generate_actor())
        return matter

    def create_atom(self):
        """

        """

        atom = Atom()
        self.atoms.append(atom)
        return atom

    def create_force(self):
        """

        """

        force = RadialForce()
        force.set_bezier_curve({
            "min_x": 0,
            "max_x": 10,
            "min_y": -10,
            "max_y": 10,
            "degree": 3,
            "ys": [0, 1, -1, 3]
        })

        self.forces.append(force)
        return force

    def create_radial_force(self, bezier_curve):
        force = RadialForce()
        force.bezier_curve = bezier_curve
        self.forces.append(force)
        return force

    @on_trait_change('matters.position')
    def positions_changed(self, arg1, arg2, arg3):
        self.scene.render()
        print "The time to update callable"
        print arg1
        print arg2
        print arg3

    def next_step(self):
        """
        This method evaluates entire universe along the time
        """

        ps = [matter.position for matter in self.matters]
        fs = [force.function() for force in self.forces]

        # Nu stands for the greek letter, that is used to described measure of something
        Nu = Matrix(len(self.matters),
                    len(self.atoms),
                    lambda i, j: self.matters[i].atoms.get(self.atoms[j], 0))

        # G stands for "generated functions"
        G = Matrix(len(self.atoms),
                   len(self.forces),
                   lambda i, j: 1 if self.forces[j] in self.atoms[i].produced_forces else 0)

        E = Matrix(len(self.forces),
                   len(self.atoms),
                   lambda i, j: 1 if self.atoms[j] in self.forces[i].atoms_to_produce_effect_on else 0)

        x, y = symbols('x y')

        F = Matrix(len(ps),
                   len(fs),
                   lambda i, j: fs[j].subs(x, x-ps[i][0]).subs(y, y-ps[i][1]))

        # P stands for potential
        P = [Matrix(1, len(ps), lambda i, j: 0 if j == k else 1)*((Nu*G).multiply_elementwise(F)) for k in xrange(0, len(ps))]

        # Every P[i] is a vector of potentials that affect i-th matter

        # Let us reduce this potential against weighted against
        # force affect on atoms and number of atoms in specific matter
        M = [(P[i]*E*Nu[i, :].T)[0] for i in xrange(0, len(ps))]

        grad_M_u = [vectorize(lambdify((x, y), diff(M[i], x), "numpy")) for i in xrange(len(ps))]
        grad_M_v = [vectorize(lambdify((x, y), diff(M[i], y), "numpy")) for i in xrange(len(ps))]

        for mi, matter in enumerate(self.matters):
            (x, y) = matter.position
            matter.position = tuple(array((grad_M_u[mi](x, y), grad_M_v[mi](x, y))) + array((x, y)))

    @on_trait_change('scene')
    def bind_to_scene(self, scene):
        """
        This method binds TVTK actors associated
        with visual objects to scene
        """

        for matter in self.matters:
            scene.add_actor(matter.generate_actor())
