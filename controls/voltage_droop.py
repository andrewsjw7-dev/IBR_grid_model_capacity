"""
Voltage-reactive power droop controller.

Implements:

    V* = V0 - kq(Q-Q0)

"""

from controls.controller import Controller



class VoltageDroopController(Controller):


    def __init__(
            self,
            V0,
            Q0,
            kq):

        super().__init__()

        self.V0 = V0

        self.Q0 = Q0

        self.kq = kq



    def output(self, measurements):

        """
        Calculate voltage reference.

        measurements requires:

            Q

        """

        Q = measurements["Q"]


        V_star = (

            self.V0

            -

            self.kq*(Q-self.Q0)

        )


        return V_star