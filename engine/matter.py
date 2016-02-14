from numpy import array, zeros, uint8, float64
import yaml

from atom import Atom


class Matter(object):
    """
    Any physical object we consider to be a Matter.
    """

    def __init__(self):
        self.position = (0.0, 0.0)
        self.atoms = dict()
        self.name = ''
        self.color = (0.0, 0.0, 0.0)
        self.vector_field_is_visible = False


def matter_representer(dumper, matter):
    (x, y) = matter.position
    return dumper.represent_mapping(u'!Matter', {"name": matter.name,
                                                 "position": [float(x), float(y)],
                                                 "atoms": dict(matter.atoms),
                                                 "color": list(matter.color),
                                                 "vector_field_is_visible": matter.vector_field_is_visible,
                                                 })


def matter_constructor(loader, node):
    matter = Matter()
    yield matter
    mapping = loader.construct_mapping(node, deep=True)
    matter.name = mapping["name"]
    matter.position = tuple(array(mapping["position"]))
    matter.atoms = mapping["atoms"]
    matter.color = tuple(mapping["color"])
    matter.vector_field_is_visible = mapping["vector_field_is_visible"]

yaml.add_representer(Matter, matter_representer)
yaml.add_constructor(u'!Matter', matter_constructor)
