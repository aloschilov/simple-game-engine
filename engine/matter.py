from traits.api import (Array, Dict, Float, String, RGBColor, Bool)
from tvtk.api import tvtk
from traits.api import HasTraits, Instance, on_trait_change
from numpy import array, zeros, uint8, float64
import yaml

from atom import Atom

from atoms_quantities_to_image import atoms_quantities_to_image


class Matter(HasTraits):
    """
    Any physical object we consider to be a Matter.
    """

    position = Array('d', (2,), labels=['x', 'y'], cols=2,
                     desc='Position of an object in 2D-space')
    atoms = Dict(key_trait=Instance(Atom), value_trait=Float)

    actor = Instance(tvtk.Actor)

    name = String()

    color = RGBColor((0.0, 0.0, 0.0))

    vector_field_is_visible = Bool(False)

    @on_trait_change('position')
    def update_position(self, affected_object):
        """
        Make visualization position consistent with model
        """

        if self.actor is None:
            return

        if affected_object is self.position:
            (x, y) = (self.position[0], self.position[1])
            self.actor.position = (x, y, 0)
            self.update_legend_image()

    @on_trait_change('color')
    def update_color(self, color):
        if color is self.color:
            p = tvtk.Property(color=color)
            self.actor.property = p

    def generate_actor(self):
        """
        Temporary way to generate an actor for matter
        It does not take into consideration variety of options
        the actor could be created, the way of atoms visualisation
        an so on.
        """

        self.sphere = tvtk.SphereSource(center=(0, 0, 0), radius=0.5)
        sphere_mapper = tvtk.PolyDataMapper(input=self.sphere.output)
        p = tvtk.Property(opacity=0.4, color=self.color)
        self.actor = tvtk.Actor(mapper=sphere_mapper, property=p)

        return self.actor

    def generate_legend_actor(self):
        """

        :return:
        :rtype: tvtk.Actor
        """

        data_matrix = atoms_quantities_to_image([("name 1", 20), ("name 2", 30)], self.name)

        self.legend_actor = tvtk.ImageActor()
        self.legend_image_import = tvtk.ImageImport()
        self.update_legend_image()
        self.legend_actor.input = self.legend_image_import.output

        return self.legend_actor

    @on_trait_change('atoms+')
    def update_legend_image(self):

        if not hasattr(self, 'legend_image_import'):
            return

        image = atoms_quantities_to_image(
            zip([atom.name for atom in self.atoms.keys()], self.atoms.values()), self.name)

        w, h, _ = image.shape

        data_matrix = image.astype(uint8).transpose(1, 0, 2)
        data_string = data_matrix.tostring()

        self.legend_image_import.copy_import_void_pointer(data_string, len(data_string))
        self.legend_image_import.set_data_scalar_type_to_unsigned_char()
        self.legend_image_import.number_of_scalar_components = 4
        self.legend_image_import.data_extent = (0, w-1, 0, h-1, 0, 0)
        self.legend_image_import.whole_extent = (0, w-1, 0, h-1, 0, 0)

        self.legend_image_import.update()

        x, y, _ = image.shape
        pos_x, pos_y = self.position
        transform = tvtk.Transform()
        transform.translate((pos_x, pos_y, 0.0))
        transform.rotate_z(-90)
        transform.translate((-5.0/2.0, -5.0/2.0, 0.0))
        transform.scale((5.0/x, 5.0/y, 1.0))
        self.legend_actor.user_transform = transform


def matter_representer(dumper, matter):
    (x, y) = matter.position
    return dumper.represent_mapping(u'!Matter', {"name": matter.name,
                                                 "position": [float(x), float(y)],
                                                 "atoms": dict(matter.atoms),
                                                 "color": list(matter.color)
                                                 })


def matter_constructor(loader, node):
    matter = Matter()
    yield matter
    mapping = loader.construct_mapping(node, deep=True)
    matter.name = mapping["name"]
    matter.position = tuple(array(mapping["position"]))
    matter.atoms = mapping["atoms"]
    matter.color = tuple(mapping["color"])

yaml.add_representer(Matter, matter_representer)
yaml.add_constructor(u'!Matter', matter_constructor)
