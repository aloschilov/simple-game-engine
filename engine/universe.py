from enthought.traits.api import HasTraits, Instance, List

from engine.matter import Matter


class Universe(HasTraits):
    """
    A hypothetic Universe, where in its 2d Space, Forces
    control what happen. There is Matter build out of different
    Atoms able to move. Each Atom affect the Forces.
    The NaturalLaws define how Atoms convert into other Atoms,
    if certain Forces are present.
    """

    matters = List(trait=Instance(Matter))

    def next_step(self):
        """
        This method evaluates entire universe along the time
        """

        for matter in self.matters:
            (x, y) = matter.position
            x += 00000000000000.1
            y += 00000000000000.1
            matter.position = (x, y)
            print "Good to see that position is updated {position}".format(position=matter.position)


    def bind_to_scene(self, scene):
        """
        This method binds TVTK actors accossiated
        with visual objects to scene
        """

        for matter in self.matters:
            scene.add_actor(matter.generate_actor())
