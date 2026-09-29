"""
Results object returned by every simulation.

This wraps the SciPy OdeResult and provides useful
analysis and plotting routines.
"""

import numpy as np
import matplotlib.pyplot as plt


class Results:

    def __init__(self, solution, model):

        self.solution = solution
        self.model = model
        self.t = solution.t

        self.x = solution.y

        self.state_names = model.state_names
    # ---------------------------------------

    @property
    def n_states(self):

        return self.x.shape[0]

    # ---------------------------------------

    @property
    def n_points(self):

        return self.x.shape[1]

    # ---------------------------------------

    @property
    def duration(self):

        return self.t[-1] - self.t[0]

    # ---------------------------------------

    def state(self, index):

        """
        Return one state.
        """

        return self.x[index]

    # ---------------------------------------

    def plot_state(
            self,
            index,
            xlabel="Time (s)",
            ylabel=None):

        plt.figure(figsize=(8,4))

        plt.plot(
            self.t,
            self.state(index)
        )

        plt.xlabel(xlabel)

        if ylabel is not None:

            plt.ylabel(ylabel)

        plt.grid(True)

        plt.tight_layout()

        plt.show()

    # ---------------------------------------

    def phase_plane(
            self,
            x_index,
            y_index):

        plt.figure(figsize=(6,6))

        plt.plot(
            self.state(x_index),
            self.state(y_index)
        )

        plt.xlabel(f"x{x_index}")

        plt.ylabel(f"x{y_index}")

        plt.grid(True)

        plt.axis("equal")

        plt.tight_layout()

        plt.show()

    # ---------------------------------------

    def summary(self):

        print()

        print("Simulation Results")

        print("------------------")

        print(f"Duration : {self.duration:.3f} s")

        print(f"States   : {self.n_states}")

        print(f"Points   : {self.n_points}")

        print()
    
    
    def state(self, name):

        if isinstance(name, int):
    
            return self.x[name]
    
        index = self.state_names.index(name)
    
        return self.x[index]
    
    
    def __getitem__(self, key):

        return self.state(key)
    
    
    def frequency(self, omega_state="omega"):

        omega = self.state(omega_state)
    
        return omega/(2*np.pi)
    
    
    def plot_frequency(self):
    
        plt.figure(figsize=(8,4))
    
        plt.plot(
            self.t,
            self.frequency()
        )
    
        plt.xlabel("Time (s)")
    
        plt.ylabel("Frequency (Hz)")
    
        plt.grid(True)
    
        plt.tight_layout()
    
        plt.show()