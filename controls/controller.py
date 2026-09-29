"""
Base controller class.

Controllers convert measurements into commands.

General form:

        u = C(y)

where:

    y = measured variables

    u = control output


Examples:

    Droop controller:

        omega -> P reference


    PLL:

        voltage -> angle estimate


    Current controller:

        current error -> voltage command


This class defines the interface only.
"""




class Controller:


    def __init__(self):

        """
        Base controller.

        Specific controllers will add
        their own parameters.
        """

        pass



    def output(self, measurements):

        """
        Calculate controller output.


        Parameters
        ----------
        measurements :
            Dictionary or vector containing
            measured signals.


        Returns
        -------
        control output


        This function must be implemented
        by derived controllers.

        """


        raise NotImplementedError(

            "Controller subclasses must implement output()"

        )