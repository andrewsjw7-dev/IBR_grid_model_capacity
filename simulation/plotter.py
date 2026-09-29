"""
simulation/plotter.py

Plotting utilities for simulation results.

Compatible with:

    simulation.results.Results

Provides:

    plot_states()
    plot_state(name)

"""


import matplotlib.pyplot as plt



class Plotter:


    def __init__(self, results):

        """
        Parameters
        ----------
        results :
            simulation.results.Results object

        """

        self.results = results


        self.t = results.t

        self.x = results.x

        self.state_names = results.state_names



    # =================================================
    # Plot all states
    # =================================================

    def plot_states(self):

        """
        Plot every state trajectory.

        """

        n_states = self.x.shape[0]


        plt.figure(figsize=(10,6))


        for i in range(n_states):


            plt.plot(

                self.t,

                self.x[i,:],

                label=self.state_names[i]

            )


        plt.xlabel(

            "Time (s)"

        )


        plt.ylabel(

            "State"

        )


        plt.title(

            "Dynamic States"

        )


        plt.legend()


        plt.grid(True)


        plt.tight_layout()


        plt.show()



    # =================================================
    # Plot single state
    # =================================================

    def plot_state(
            self,
            name):

        """
        Plot one state by name.

        Example:

            plotter.plot_state(
                "SG1_omega"
            )

        """


        if name not in self.state_names:


            raise ValueError(

                f"Unknown state '{name}'.\n"

                f"Available states:\n"

                f"{self.state_names}"

            )



        index = self.state_names.index(name)



        plt.figure(figsize=(8,4))


        plt.plot(

            self.t,

            self.x[index,:]

        )


        plt.xlabel(

            "Time (s)"

        )


        plt.ylabel(

            name

        )


        plt.title(

            name

        )


        plt.grid(True)


        plt.tight_layout()


        plt.show()



    # =================================================
    # Compare frequencies
    # =================================================

    def plot_frequency_states(self):

        """
        Convenience function.

        Plots all states containing:

            omega

        """


        indices = [

            i

            for i,name in enumerate(self.state_names)

            if "omega" in name

        ]



        plt.figure(figsize=(8,4))


        for i in indices:


            plt.plot(

                self.t,

                self.x[i,:],

                label=self.state_names[i]

            )



        plt.xlabel(

            "Time (s)"

        )


        plt.ylabel(

            "Frequency (rad/s)"

        )


        plt.title(

            "Frequency Dynamics"

        )


        plt.legend()


        plt.grid(True)


        plt.tight_layout()


        plt.show()