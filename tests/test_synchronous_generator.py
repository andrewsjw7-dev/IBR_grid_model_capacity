import numpy as np

from models.synchronous_generator import SynchronousGenerator

from simulation.solver import Simulation

from simulation.plotter import Plotter



f0 = 50

omega0 = 2*np.pi*f0



generator = SynchronousGenerator(

    M=8.0,

    D=1.5,

    Pm=0.8,

    Pmax=1.5,

    omega0=omega0

)



# Equilibrium angle

delta0 = np.arcsin(
    0.8/1.5
)



x0 = [

    delta0,

    omega0

]



simulation = Simulation(

    model=generator,

    t_start=0,

    t_end=20,

    n_points=2000

)


results = simulation.run(x0)


results.summary()



plotter = Plotter(results)


plotter.state(
    "delta",
    "Rotor angle (rad)"
)


plotter.frequency()