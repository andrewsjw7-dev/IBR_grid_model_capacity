"""
Base class for all dynamic models.

Every dynamic model must define

    - initial_state()
    - derivatives()

The derivatives() function accepts an optional dictionary of
electrical inputs supplied by the network.

This allows the same interface to be used for

    * synchronous generators
    * grid-forming inverters
    * grid-following inverters
    * loads
    * future dynamic devices
"""


from abc import ABC, abstractmethod

import numpy as np


class DynamicModel(ABC):

    def __init__(self):

        self.state_names = []

    # -------------------------------------------------
    # Initial conditions
    # -------------------------------------------------

    @abstractmethod
    def initial_state(self):
        """
        Return the initial state vector.

        Returns
        -------
        numpy.ndarray
        """
        pass

    # -------------------------------------------------
    # Dynamic equations
    # -------------------------------------------------

    @abstractmethod
    def derivatives(
            self,
            t,
            x,
            electrical_inputs=None):
        """
        Evaluate the state derivatives.

        Parameters
        ----------
        t : float
            Time.

        x : ndarray
            State vector.

        electrical_inputs : dict, optional

            Quantities supplied by the network.

            Typical entries are

                P
                Q
                V
                theta
                omega_coi

        Returns
        -------
        ndarray
        """
        pass