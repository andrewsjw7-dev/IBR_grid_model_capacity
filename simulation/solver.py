"""
Generic numerical simulation engine.

Solves:

        dx/dt = f(t,x)

for any dynamic model implementing:

        model.derivatives(t,x)

The solver is independent of:

    - synchronous generators
    - grid-forming inverters
    - grid-following inverters
    - controllers
    - network topology

Disturbances are handled externally through a disturbance interface.

Examples:

    LineTrip
    LoadStep
    Fault
    GeneratorTrip
"""


import numpy as np

from scipy.integrate import solve_ivp

from simulation.results import Results



class Simulation:


    def __init__(
            self,
            model,
            disturbances=None,
            t_start=0.0,
            t_end=10.0,
            n_points=1000,
            method="RK45",
            rtol=1e-8,
            atol=1e-10):

        """
        Create a simulation.

        Parameters
        ----------
        model :
            DynamicModel object

        disturbances :
            List of disturbance objects

        t_start :
            Simulation start time

        t_end :
            Simulation end time

        n_points :
            Number of output points

        method :
            scipy integration method

        rtol :
            Relative tolerance

        atol :
            Absolute tolerance
        """


        self.model = model


        if disturbances is None:

            disturbances = []


        self.disturbances = disturbances


        self.t_start = t_start

        self.t_end = t_end

        self.n_points = n_points

        self.method = method

        self.rtol = rtol

        self.atol = atol



    # =================================================
    # Disturbance handling
    # =================================================

    def apply_disturbances(
            self,
            t):

        """
        Apply all disturbances at time t.

        Parameters
        ----------
        t :
            Current simulation time
        """


        for disturbance in self.disturbances:

            disturbance.apply(

                t,

                self.model

            )



    # =================================================
    # ODE wrapper
    # =================================================

    def rhs(
            self,
            t,
            x):

        """
        Wrapper passed to solve_ivp.

        Applies disturbances before evaluating
        the dynamic model.
        """


        self.apply_disturbances(t)


        return self.model.derivatives(

            t,

            x

        )



    # =================================================
    # Run simulation
    # =================================================

    def run(
            self,
            x0):

        """
        Run the simulation.

        Parameters
        ----------
        x0 :
            Initial state vector


        Returns
        -------
        Results
        """


        #
        # Reset disturbances before each run
        #

        for disturbance in self.disturbances:
            try:
                disturbance.reset(self.model)
            except TypeError:
                disturbance.reset()
        if hasattr(self.model, "update_network"):
            self.model.update_network()



        t_eval = np.linspace(

            self.t_start,

            self.t_end,

            self.n_points

        )



        solution = solve_ivp(

            fun=self.rhs,

            t_span=(

                self.t_start,

                self.t_end

            ),

            y0=x0,

            t_eval=t_eval,

            method=self.method,

            rtol=self.rtol,

            atol=self.atol

        )



        if not solution.success:

            raise RuntimeError(

                solution.message

            )



        return Results(

            solution,

            self.model

        )



    # =================================================
    # Summary
    # =================================================

    def summary(self):

        """
        Print simulation settings.
        """


        print()

        print("Simulation")

        print("----------------")


        print(

            f"Start : {self.t_start}"

        )


        print(

            f"End   : {self.t_end}"

        )


        print(

            f"Points: {self.n_points}"

        )


        print(

            f"Solver: {self.method}"

        )


        if self.disturbances:

            print()

            print("Disturbances")

            for disturbance in self.disturbances:

                print(

                    f"  {disturbance}"

                )


        print()