class Sensor(object):
    """
    Sensor perceives value of Force at the current position.
    """

    def __init__(self, agent=None, perceived_force=None):
        """
        A default constructor of Sensor, which could be provided
        with reference to parent Agent.
        
        :param agent: parent Agent to which this Sensor belongs
        :type agent: Agent
        """

        # a position relative to an Agent
        self.position = (0.0, 0.0)

        self.agent = agent
        self.perceived_force = perceived_force


class Agent(object):
    """
    Agents perceive Forces via Sensors
    """

    def __init__(self, universe=None):
        """

        :param universe: a reference to parenting Universe
        :type universe: Universe
        """

        # We need a reference to the Universe
        # in order to query Sensor values
        self.position = (0.0, 0.0)
        self.name = ""
