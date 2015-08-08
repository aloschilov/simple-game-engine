from engine import Universe

import yaml

universe = Universe()
matter_a = universe.create_matter()
matter_a.name = "Matter A"
matter_b = universe.create_matter()
matter_b.name = "Matter B"

atom_a = universe.create_atom()
atom_a.name = "Atom A"
atom_b = universe.create_atom()
atom_b.name = "Atom B"

matter_a.atoms[atom_a] = 10
matter_a.atoms[atom_b] = 20

matter_b.atoms[atom_a] = 30
matter_b.atoms[atom_b] = 40

force_a = universe.create_force()
force_b = universe.create_expression_based_force("x**2.0 + y**2.0")
atom_a.produced_forces.append(force_a)

natural_law = universe.create_natural_law()
natural_law.atom_in = atom_a
natural_law.atom_out = atom_b
natural_law.accelerator = force_a
natural_law.multiplicative_component = 0.1
natural_law.additive_component = 3.2

stream = file('universe.yaml', 'w')
serialized_object = yaml.dump(universe, stream)
