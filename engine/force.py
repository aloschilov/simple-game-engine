class Force(object):
    """
    Force affects atoms.
    """

    def __init__(self):
        self.atoms_to_produce_effect_on = list()
        self.name = ""

    def function(self):
        """
        :return: callable with 2D-point as a parameter and value of the function as a result
        """
        raise NotImplemented

