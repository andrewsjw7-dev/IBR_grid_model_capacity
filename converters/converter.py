"""
Average converter model.

Represents inverter dynamics without
individual PWM switching.

Equation:

    tau * du/dt = u_ref - u

"""



class Converter:


    def __init__(
            self,
            tau):

        """
        Parameters
        ----------
        tau :
            Converter time constant (s)
        """

        self.tau = tau



    def derivative(
            self,
            u,
            u_ref):

        """
        Converter output derivative.
        """


        return (

            u_ref-u

        ) / self.tau