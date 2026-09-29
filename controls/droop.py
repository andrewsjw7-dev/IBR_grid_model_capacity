"""
Active power-frequency droop controller.

Implements:

        P* = P0 - kp(omega - omega0)


where:

    P*
        power command

    P0
        nominal power reference

    kp
        droop gain

    omega
        measured angular frequency

    omega0
        nominal angular frequency


This is the simplest form of
grid-forming control.
"""


from controls.controller import Controller




class DroopController(Controller):


    def __init__(
            self,
            P0,
            kp,
            omega0):

        """
        Parameters
        ----------
        P0 :
            Nominal active power reference (pu)

        kp :
            Frequency droop coefficient

        omega0 :
            Nominal angular frequency (rad/s)

        """


        super().__init__()


        self.P0 = P0

        self.kp = kp

        self.omega0 = omega0



    def output(self, measurements):

        """
        Calculate power reference.

        Parameters
        ----------
        measurements :
            Dictionary containing:

                omega


        Returns
        -------
        P_star :
            Active power command


        Implements:

            P*=P0-kp(omega-omega0)

        """


        omega = measurements["omega"]



        P_star = (

            self.P0

            -

            self.kp*(omega-self.omega0)

        )


        return P_star