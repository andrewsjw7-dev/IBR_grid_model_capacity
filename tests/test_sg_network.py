"""
Test:

    Synchronous Generator
            |
        Network
            |
      Infinite Bus


States:

    delta
    omega

"""


import numpy as np


from models.network import Network

from models.synchronous_generator import SynchronousGenerator


from simulation.solver import Simulation

from simulation.plotter import Plotter




# ==================================================
# Frequency
# ==================================================

F0 = 50.0

OMEGA0 = 2*np.pi*F0




# ==================================================
# Create network
# ==================================================

network = Network()




# ==================================================
# Create generator
# ==================================================

generator = SynchronousGenerator(

    M=8.0,

    D=1.5,

    Pm=0.8,

    Pmax=1.5,

    omega0=OMEGA0,

    network=network

)



# ==================================================
# Initial equilibrium
# ==================================================

delta0 = np.arcsin(

    0.8/1.5

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

    t_start=0,

    t_end=20,

    n_points=4000

)



simulation.summary()



results = simulation.run(x0)



results.summary()




# ==================================================
# Plot
# ==================================================

plotter = Plotter(results)



plotter.frequency()



plotter.state(

    "delta",

    ylabel="Rotor angle (rad)"

)