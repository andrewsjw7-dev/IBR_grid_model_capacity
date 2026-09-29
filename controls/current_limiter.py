"""
Current limiter for inverter protection.

Limits current magnitude:

    |I| <= Imax

"""


import numpy as np



class CurrentLimiter:


    def __init__(
            self,
            Imax):

        self.Imax = Imax



    def limit(self, I):

        """
        Saturate current.

        """

        magnitude = abs(I)


        if magnitude <= self.Imax:

            return I


        return (

            I / magnitude

        ) * self.Imax