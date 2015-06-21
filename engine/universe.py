from traits.api import HasTraits, Instance, List, on_trait_change
from sympy import Matrix, symbols
from sympy.physics.vector import ReferenceFrame, gradient
from numpy import array, zeros, uint8
from mayavi.core.ui.api import MlabSceneModel
from tvtk.api import tvtk
from pykka.actor import ActorRef

from . import Atom
from . import RadialForce
from . import Force
from . import Matter
from vector_field_rendering_actor import VectorFieldRenderingActor


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
    vector_field_rendering_actor = Instance(ActorRef, None)

    def __init__(self):
        super(Universe, self).__init__()
        self.vector_field_rendering_countdown = 0
        self.future = None
        self.image_actor = tvtk.ImageActor()
        self.image_import = tvtk.ImageImport()

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
        #print "The time to update callable"
        #print arg1
        #print arg2
        #print arg3

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

        R = ReferenceFrame('R')
        M = [(P[i]*E*Nu[i, :].T)[0].subs(x, R[0]).subs(y, R[1]) for i in xrange(0, len(ps))]
        W = [gradient(M[i], R).to_matrix(R).subs({R[0]: x, R[1]: y})[:2] for i in xrange(len(ps))]

        if self.vector_field_rendering_actor is not None:
            if self.vector_field_rendering_countdown == 0:
                if self.future is not None:
                    image = self.future.get()
                    if image is not None:
                        print "Render"
                        self.render_force_image(image)

                self.vector_field_rendering_countdown = 100
                self.future = self.vector_field_rendering_actor.ask({"W": W, "bounding_rect": (-10, 10, 10, -10)}, block=False)
            else:
                self.vector_field_rendering_countdown -= 1

        delta_t = 1

        for mi, matter in enumerate(self.matters):
            (x_v, y_v) = matter.position
            (x_, y_) = tuple(array((
                float(W[mi][0].subs({x : x_v, y : y_v}))*delta_t,
                float(W[mi][1].subs({x : x_v, y : y_v}))*delta_t
            )) +
                             array((x_v, y_v)))
            x_ = x_ if x_ > -10 else -10
            x_ = x_ if x_ < 10 else 10
            y_ = y_ if y_ > -10 else -10
            y_ = y_ if y_ < 10 else 10
            matter.position = (x_, y_)

    @on_trait_change('scene')
    def bind_to_scene(self, scene):
        """
        This method binds TVTK actors associated
        with visual objects to scene
        """

        for matter in self.matters:
            scene.add_actor(matter.generate_actor())

        if self.vector_field_rendering_actor is None:
            print "Launching VectorFieldRenderingActor"
            self.initialize_image_import_with_empty_image()
            self.scene.add_actor(self.image_actor)
            self.image_actor.input = self.image_import.output
            self.vector_field_rendering_actor = VectorFieldRenderingActor.start()

    def render_force_image(self, image):
        self.update_image(image)
        x, y, _ = image.shape
        transform = tvtk.Transform()
        transform.rotate_z(-90)
        transform.translate((-20.0/2.0, -20.0/2.0, 0.0))
        transform.scale((20.0/x, 20.0/y, 1.0))
        self.image_actor.user_transform = transform

    def update_image(self, image):
        """
        This call updates vtkImageImport with a new image
        :param image:
        :return:
        """

        w, h, _ = image.shape

        data_matrix = image.astype(uint8).transpose(1, 0, 2)
        data_string = data_matrix.tostring()

        self.image_import.copy_import_void_pointer(data_string, len(data_string))
        self.image_import.set_data_scalar_type_to_unsigned_char()
        self.image_import.number_of_scalar_components = 4
        self.image_import.data_extent = (0, w-1, 0, h-1, 0, 0)
        self.image_import.whole_extent = (0, w-1, 0, h-1, 0, 0)

        self.image_import.update()

    def initialize_image_import_with_empty_image(self):
        data_matrix = zeros([75, 75, 1], dtype=uint8)
        data_string = data_matrix.tostring()
        self.image_import.copy_import_void_pointer(data_matrix, len(data_string))
        self.image_import.set_data_scalar_type_to_unsigned_char()
        self.image_import.number_of_scalar_components = 1
        self.image_import.data_extent = (0, 74, 0, 74, 0, 0)
        self.image_import.whole_extent = (0, 74, 0, 74, 0, 0)

        self.image_import.update()
