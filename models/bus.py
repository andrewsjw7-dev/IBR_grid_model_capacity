"""
Bus model.

A Bus represents a node in the electrical network.

The Bus stores topology only.

Electrical quantities such as:

    - voltage magnitude
    - voltage angle
    - active power
    - reactive power

are calculated by the Network model.

"""



class Bus:


    def __init__(self, name):

        """
        Parameters
        ----------
        name : str
            Bus identifier
        """


        self.name = name


        #
        # Connected dynamic devices
        #

        self.devices = []


        #
        # Connected loads
        #

        self.loads = []



    # -------------------------------------------------
    # Components
    # -------------------------------------------------

    def add_device(self, device):

        """
        Attach a dynamic device.
        """

        self.devices.append(device)



    def add_load(self, load):

        """
        Attach a load.

        Placeholder for future dynamic/static loads.
        """

        self.loads.append(load)



    # -------------------------------------------------
    # Representation
    # -------------------------------------------------

    def __repr__(self):

        return f"Bus({self.name})"