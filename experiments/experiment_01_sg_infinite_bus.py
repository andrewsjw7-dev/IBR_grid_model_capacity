"""
Experiment 01

Classical synchronous generator
connected to an infinite bus.

Model:

        SG  ----  Infinite Bus


A disturbance is applied at t = 5 seconds:

        Pm -> Pm - 0.2 pu


This represents:

    - sudden load increase
    - generator power reduction

"""



import numpy as np


from models.synchronous_generator import SynchronousGenerator


from simulation.solver import Simulation


from simulation.plotter import Plotter




# ==================================================
# Grid frequency
# ==================================================

F0 = 50.0

OMEGA0 = 2*np.pi*F0



# ==================================================
# Disturbance model
# ==================================================


class DisturbedGenerator(SynchronousGenerator):


    def mechanical_power(self, t):

        """
        Apply a step disturbance.

        Before 5 seconds:

            Pm = 0.8 pu


        After 5 seconds:

            Pm = 0.6 pu

        """


        if t < 5.0:

            return self.Pm


        else:

            return self.Pm - 0.2




# ==================================================
# Create generator
# ==================================================


generator = DisturbedGenerator(

    M=8.0,

    D=1.5,

    Pm=0.8,

    Pmax=1.5,

    omega0=OMEGA0

)



# ==================================================
# Initial equilibrium condition
# ==================================================


delta0 = np.arcsin(

    0.8 / 1.5

)


x0 = [

    delta0,

    OMEGA0

]



# ==================================================
# Simulation
# ==================================================


simulation = Simulation(

    model=generator,

    t_start=0.0,

    t_end=20.0,

    n_points=4000

)



simulation.summary()



results = simulation.run(x0)



results.summary()



# ==================================================
# Plot results
# ==================================================


plotter = Plotter(results)



plotter.frequency()



plotter.state(

    "delta",

    ylabel="Rotor angle (rad)"

)


plotter.phase_plane(

    "delta",

    "omega"

)