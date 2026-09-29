"""
Results container for simulations.

Stores:

    t

and

    x(t)

and provides access to states.

The Results object does not perform simulation.
It only analyses simulation output.
"""


import numpy as np



class Results:


    def __init__(
            self,
            solution,
            model):


        """
        Parameters
        ----------
        solution :
            Output from scipy.solve_ivp

        model :
            DynamicModel that generated solution
        """


        self.solution = solution

        self.model = model


        # Time vector

        self.t = solution.t


        # State trajectories

        self.x = solution.y


        # State names supplied by model

        self.state_names = model.state_names



    # --------------------------------------------------
    # Basic information
    # --------------------------------------------------


    @property
    def n_states(self):

        return self.x.shape[0]



    @property
    def n_points(self):

        return self.x.shape[1]



    @property
    def duration(self):

        return self.t[-1]-self.t[0]



    # --------------------------------------------------
    # State access
    # --------------------------------------------------


    def state(self, name):

        """
        Retrieve a state.

        Can use:

            results.state(0)

        or:

            results.state("delta")

        """


        if isinstance(name, int):

            return self.x[name]


        if name not in self.state_names:

            raise ValueError(

                f"Unknown state '{name}'. "
                f"Available states: {self.state_names}"

            )


        index = self.state_names.index(name)


        return self.x[index]



    # Allow:

    # results["delta"]

    def __getitem__(self, name):

        return self.state(name)



    # --------------------------------------------------
    # Frequency conversion
    # --------------------------------------------------


    def frequency(
            self,
            omega_state="omega"):

        """
        Convert angular velocity:

            omega rad/s

        into:

            frequency Hz
        """


        omega = self.state(omega_state)


        return omega/(2*np.pi)



    # --------------------------------------------------
    # Summary
    # --------------------------------------------------


    def summary(self):

        print()

        print("Simulation Results")

        print("------------------")


        print(
            f"Duration : {self.duration:.3f} s"
        )


        print(
            f"States   : {self.n_states}"
        )


        print(
            f"Points   : {self.n_points}"
        )


        print(
            f"State names:"
        )


        for i,name in enumerate(self.state_names):

            print(
                f"  {i}: {name}"
            )


        print()
        
    # --------------------------------------------------
    # Final state
    # --------------------------------------------------

    def final_state(self):
        """
        Return final simulation state vector.

        Returns
        -------
        numpy.ndarray

            x(t_final)

        """

        return self.x[:, -1]



    # --------------------------------------------------
    # Initial state
    # --------------------------------------------------

    def initial_state(self):
        """
        Return initial simulation state vector.
        """

        return self.x[:, 0]



    # --------------------------------------------------
    # State matrix
    # --------------------------------------------------

    def state_history(self):
        """
        Return complete state trajectory.

        Shape:

            (n_states, n_time_points)

        """

        return self.x



    # --------------------------------------------------
    # Plot interface
    # --------------------------------------------------

    def plot_states(self):

        import matplotlib.pyplot as plt
    
    
        for i,name in enumerate(self.state_names):
    
            plt.figure()
    
            plt.plot(
    
                self.t,
    
                self.x[i]
    
            )
    
            plt.xlabel("Time (s)")
    
            plt.ylabel(name)
    
            plt.title(name)
    
            plt.grid()
    
            plt.show()