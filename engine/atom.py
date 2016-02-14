import yaml


class Atom(object):
    """
    Everything in Universe consists of Atoms.
    """

    def __init__(self):
        self.name = ''
        self.produced_forces = list()

def atom_representer(dumper, atom):
    return dumper.represent_mapping(u'!Atom', {"name": atom.name,
                                               "produced_forces": list(atom.produced_forces),
                                               })


def atom_constructor(loader, node):
    atom = Atom()
    yield atom
    mapping = loader.construct_mapping(node, deep=True)
    atom.name = mapping["name"]
    atom.produced_forces = mapping["produced_forces"]


yaml.add_representer(Atom, atom_representer)
yaml.add_constructor(u'!Atom', atom_constructor)
