"""
Transmission line model.

The Line stores network topology only.

Electrical calculations are performed by:

    models.network.Network

"""



class Line:


    def __init__(
            self,
            from_bus,
            to_bus,
            reactance):


        """
        Parameters
        ----------
        from_bus :
            Sending bus


        to_bus :
            Receiving bus


        reactance :
            Line reactance (pu)

        """


        self.from_bus = from_bus

        self.to_bus = to_bus

        self.X = reactance
        
        self.in_service = True



    @property
    def reactance(self):

        """
        Readable alias.
        """

        return self.X



    def __repr__(self):

        return (

            f"Line({self.from_bus.name}"

            f"->{self.to_bus.name}, "

            f"X={self.X})"

        )