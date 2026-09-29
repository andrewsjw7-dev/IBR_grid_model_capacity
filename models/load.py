"""
models/load.py

Static load model.

A load is connected to a Bus and contributes
algebraic active and reactive power demand.

Convention:

    P > 0  : consumption
    Q > 0  : reactive consumption


Current model:

    Constant Power Load (PQ)


Future extensions:

    - ZIP load
    - induction motor load
    - dynamic load recovery
    - frequency-dependent load
    - voltage-dependent load


"""



class Load:


    def __init__(
            self,
            name,
            P,
            Q=0.0):


        """
        Parameters
        ----------
        name :
            Load identifier


        P :
            Active power demand (pu)


        Q :
            Reactive power demand (pu)

        """


        self.name = name


        self.P = P


        self.Q = Q



        #
        # Bus assigned later
        #

        self.bus = None



    # =================================================
    # Connection
    # =================================================

    def connect_to_bus(
            self,
            bus):

        """
        Attach load to a bus.
        """

        self.bus = bus



    # =================================================
    # Power
    # =================================================

    def active_power(self):

        """
        Active power demand.

        Positive = consumption
        """

        return self.P



    def reactive_power(self):

        """
        Reactive power demand.

        Positive = consumption
        """

        return self.Q



    def current_draw(self, Vbus):

        """Return complex current drawn from the bus by this PQ load."""

        if abs(Vbus) < 1e-8:
            raise RuntimeError("Constant-PQ load current is singular at near-zero voltage.")

        return complex(self.P, -self.Q) / complex(Vbus).conjugate()


    # =================================================
    # Representation
    # =================================================

    def __repr__(self):

        return (

            f"Load({self.name}, "

            f"P={self.P}, "

            f"Q={self.Q})"

        )