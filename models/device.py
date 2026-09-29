"""
Base class for every grid-connected device.
"""


import numpy as np

from models.dynamic_model import DynamicModel


class Device(DynamicModel):

    def __init__(
            self,
            name,
            inertia=0.0):

        super().__init__()

        self.name = name

        self.inertia = inertia

        # Assigned by Grid when the device is added
        self.bus = None

    # -------------------------------------------------
    # Grid connection
    # -------------------------------------------------

    def connect_to_bus(self, bus):

        self.bus = bus

    # -------------------------------------------------
    # Initial conditions
    # -------------------------------------------------

    def initial_state(self):

        raise NotImplementedError(

            f"{self.__class__.__name__} must implement initial_state()."

        )

    # -------------------------------------------------
    # Dynamic equations
    # -------------------------------------------------

    def derivatives(
            self,
            t,
            x,
            electrical_inputs=None):

        raise NotImplementedError(

            f"{self.__class__.__name__} must implement derivatives()."

        )

    # -------------------------------------------------
    # Frequency interface
    # -------------------------------------------------

    def frequency(self, x):

        raise NotImplementedError(

            f"{self.__class__.__name__} must implement frequency()."

        )

    # -------------------------------------------------
    # Voltage interface
    # -------------------------------------------------

    def voltage(self, x):
        """
        Return terminal voltage magnitude.

        Default implementation is 1 pu.

        Devices with internal voltage states
        (e.g. GFM) should override this.
        """
        return 1.0

    # -------------------------------------------------
    # Rotor angle interface
    # -------------------------------------------------

    def angle(self, x):
        """
        Return electrical angle.

        Assumes the first state is delta.
        """
        return x[0]