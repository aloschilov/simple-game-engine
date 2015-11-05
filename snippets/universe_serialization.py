from engine import Universe

import yaml

universe = Universe()

ball_matter = universe.create_matter()
ball_matter.name = "Ball matter"

right_wall_matter = universe.create_matter()
right_wall_matter.name = "Right wall matter"

left_wall_matter = universe.create_matter()
left_wall_matter.name = "Left wall matter"

up_wall_matter = universe.create_matter()
up_wall_matter.name = "Up wall matter"

down_wall_matter = universe.create_matter()
down_wall_matter.name = "Down wall matter"

move_x = universe.create_atom()
move_x.name = "Move X"
negative_move_x = universe.create_atom()
negative_move_x.name = "Negative move x"

move_y = universe.create_atom()
move_y.name = "Move Y"
negative_move_y = universe.create_atom()
negative_move_y.name = "Negative move y"

ball_matter.atoms[move_x] = 1
ball_matter.atoms[negative_move_x] = 0.0
ball_matter.atoms[move_y] = 2
ball_matter.atoms[negative_move_y] = 0.0
ball_matter.color = (0.0, 0.0, 1.0)
ball_matter.vector_field_is_visible = True

right_wall_force = universe.create_expression_based_force("Piecewise((0.0, x<-0.5), (10.0, x>=-0.5))")
right_wall_atom = universe.create_atom()
right_wall_matter.atoms[right_wall_atom] = 1.0
right_wall_matter.position = (5.0, 0.0)
right_wall_atom.produced_forces.append(right_wall_force)

left_wall_force = universe.create_expression_based_force("Piecewise((0.0, x>0.5), (10.0, x<=0.5))")
left_wall_atom = universe.create_atom()
left_wall_matter.atoms[left_wall_atom] = 1.0
left_wall_matter.position = (-5.0, 0.0)
left_wall_atom.produced_forces.append(left_wall_force)

up_wall_force = universe.create_expression_based_force("Piecewise((0.0, y<-0.5), (10.0, y>=-0.5))")
up_wall_atom = universe.create_atom()
up_wall_matter.atoms[up_wall_atom] = 1.0
up_wall_matter.position = (0.0, 5.0)
up_wall_atom.produced_forces.append(up_wall_force)

down_wall_force = universe.create_expression_based_force("Piecewise((0.0, y>0.5), (10.0, y<=0.5))")
down_wall_atom = universe.create_atom()
down_wall_matter.atoms[down_wall_atom] = 1.0
down_wall_matter.position = (0.0, -5.0)
down_wall_atom.produced_forces.append(down_wall_force)

move_x_to_negative_move_x_natural_law = universe.create_natural_law()
move_x_to_negative_move_x_natural_law.atom_in = move_x
move_x_to_negative_move_x_natural_law.atom_out = negative_move_x
move_x_to_negative_move_x_natural_law.accelerator = right_wall_force
move_x_to_negative_move_x_natural_law.multiplicative_component = 0.1

negative_move_x_to_move_x_natural_law = universe.create_natural_law()
negative_move_x_to_move_x_natural_law.atom_in = negative_move_x
negative_move_x_to_move_x_natural_law.atom_out = move_x
negative_move_x_to_move_x_natural_law.accelerator = left_wall_force
negative_move_x_to_move_x_natural_law.multiplicative_component = 0.1

move_y_to_negative_move_y_natural_law = universe.create_natural_law()
move_y_to_negative_move_y_natural_law.atom_in = move_y
move_y_to_negative_move_y_natural_law.atom_out = negative_move_y
move_y_to_negative_move_y_natural_law.accelerator = up_wall_force
move_y_to_negative_move_y_natural_law.multiplicative_component = 0.1

negative_move_y_to_move_y_natural_law = universe.create_natural_law()
negative_move_y_to_move_y_natural_law.atom_in = negative_move_y
negative_move_y_to_move_y_natural_law.atom_out = move_y
negative_move_y_to_move_y_natural_law.accelerator = down_wall_force
negative_move_y_to_move_y_natural_law.multiplicative_component = 0.1

# Movement field generator

movement_container_matter = universe.create_matter()

negative_move_x_generator_atom = universe.create_atom()
negative_move_x_generator_force = universe.create_expression_based_force("-x")
negative_move_x_generator_atom.produced_forces.append(negative_move_x_generator_force)
negative_move_x_generator_force.atoms_to_produce_effect_on.append(negative_move_x)

move_x_generator_atom = universe.create_atom()
move_x_generator_force = universe.create_expression_based_force("x")
move_x_generator_atom.produced_forces.append(move_x_generator_force)
move_x_generator_force.atoms_to_produce_effect_on.append(move_x)

negative_move_y_generator_atom = universe.create_atom()
negative_move_y_generator_force = universe.create_expression_based_force("-y")
negative_move_y_generator_atom.produced_forces.append(negative_move_y_generator_force)
negative_move_y_generator_force.atoms_to_produce_effect_on.append(negative_move_y)

move_y_generator_atom = universe.create_atom()
move_y_generator_force = universe.create_expression_based_force("y")
move_y_generator_atom.produced_forces.append(move_y_generator_force)
move_y_generator_force.atoms_to_produce_effect_on.append(move_y)

#
image_path = '/Users/aloschil/workspace/game_engine/snippets/bitmap_force_input.jpg'
bitmap_atom = universe.create_atom()
bitmap_force = universe.create_bitmap_force(image_path, (-10, -10, 20, 20))
bitmap_atom.produced_forces.append(bitmap_force)
bitmap_force.atoms_to_produce_effect_on.append(move_x)
#

movement_container_matter.atoms[negative_move_x_generator_atom] = 1.0
movement_container_matter.atoms[move_x_generator_atom] = 1.0
movement_container_matter.atoms[negative_move_y_generator_atom] = 1.0
movement_container_matter.atoms[move_y_generator_atom] = 1.0
movement_container_matter.atoms[bitmap_atom] = 1.0


#stream = file('universe.yaml', 'w')
#serialized_object = yaml.dump(universe, stream)


universe.compile()

for i in xrange(100):
    universe.next_step()
