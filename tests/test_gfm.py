"""
Test grid-forming inverter.

Model:

        GFM
         |
         |
    Infinite Bus


States:

    delta
    omega
    E


Controllers:

    P-w droop

    Q-V droop

"""


import numpy as np


from controls.droop import DroopController

from controls.voltage_droop import VoltageDroopController


from models.grid_forming_inverter import GridFormingInverter


from simulation.solver import Simulation

from simulation.plotter import Plotter




# ==================================================
# Grid frequency
# ==================================================

F0 = 50.0

OMEGA0 = 2*np.pi*F0




# ==================================================
# Active power controller
# ==================================================

power_controller = DroopController(

    P0=0.8+0.2,

    kp=20,

    omega0=OMEGA0

)




# ==================================================
# Voltage controller
# ==================================================

voltage_controller = VoltageDroopController(

    V0=1.0,

    Q0=0.0,

    kq=0.05

)




# ==================================================
# Create GFM
# ==================================================

gfm = GridFormingInverter(

    Mv=2.0,

    Dv=1.0,

    Pmax=1.5,

    omega0=OMEGA0,

    power_controller=power_controller,

    voltage_controller=voltage_controller,

    tauE=0.05

)




# ==================================================
# Initial equilibrium
# ==================================================

delta0 = np.arcsin(

    0.8/1.5

)


E0 = 1.0



x0 = [

    delta0,

    OMEGA0,

    E0

]




# ==================================================
# Simulation
# ==================================================

simulation = Simulation(

    model=gfm,

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



# Frequency response

plotter.frequency()



# Angle response

plotter.state(

    "delta",

    ylabel="Voltage angle (rad)"

)



# Internal voltage

plotter.state(

    "E",

    ylabel="Internal voltage (pu)"

)