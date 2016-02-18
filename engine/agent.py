
class Agent(object):
    """
    Agents perceive Forces and Matters
    """

    def __init__(self):

        self.sensors = dict()
        self.name = ""

    def add_sensor(self, force, position):
        """
        Places a sensor that feels specific force
        at the specified relative position.

        :param force:
        :param position:
        :return: Nothing
        """

        if force in self.sensors.keys():
            if position not in self.sensors[force]:
                self.sensors[force].append(position)
        else:
            self.sensors[force] = [position, ]

    def remove_sensor(self, force, position):
        """
        Removes a sensor that feels specific force
        at the specified relative position

        :param position: relative position of the sensor with
        respect to agent position
        :type position: (float, float)
        :param force: a Force to feel
        :type force: engine.Force
        :return: Nothing
        """

        if force in self.sensors.keys():
            if position in self.sensors[force]:
                self.sensors[force].remove(position)
        else:
            # There are no sensors exist which feel
            # specified force
            return

    def get_vision_of_force(self, force):
        """

        :param force:
        :return:
        """
        pass
