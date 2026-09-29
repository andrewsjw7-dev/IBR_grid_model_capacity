"""
test_grid.py

Two bus SG-GFM-load transient stability test.

Network:

             X = 0.2 pu

     SG ---------------- GFM
      |                   |
      |                   |
      +------ Load -------+


Tests:

    - topology
    - SG model
    - GFM model
    - static load
    - network coupling
    - COI frequency
    - simulation
    - plotting


"""
from disturbances.line_trip import LineTrip


import numpy as np



# ==================================================
# Imports
# ==================================================


from models.bus import Bus

from models.line import Line

from models.load import Load

from models.grid import Grid


from models.synchronous_generator import (
    SynchronousGenerator
)


from models.grid_forming_inverter import (
    GridFormingInverter
)



from controls.droop import (
    DroopController
)


from controls.voltage_droop import (
    VoltageDroopController
)



from simulation.solver import Simulation

from simulation.plotter import Plotter





# ==================================================
# Parameters
# ==================================================


omega0 = 2*np.pi*50



# ==================================================
# Create buses
# ==================================================


bus1 = Bus(
    "Bus1"
)



bus2 = Bus(
    "Bus2"
)





# ==================================================
# Create transmission line
# ==================================================


line = Line(

    bus1,

    bus2,

    reactance=0.2

)





# ==================================================
# Create Grid
# ==================================================


grid = Grid()



grid.add_bus(bus1)

grid.add_bus(bus2)



grid.add_line(line)





# ==================================================
# Controllers
# ==================================================


power_controller = DroopController(

    P0=1.0,

    kp=0.05,

    omega0=omega0

)



voltage_controller = VoltageDroopController(

    V0=1.0,

    Q0=0.0,

    kq=0.05

)





# ==================================================
# Create synchronous generator
# ==================================================


sg = SynchronousGenerator(

    name="SG1",

    M=5.0,

    D=1.0,

    Pm=1.0,

    Pmax=2.0,

    omega0=omega0

)





# ==================================================
# Create grid forming inverter
# ==================================================


gfm = GridFormingInverter(

    name="GFM1",

    Mv=2.0,

    Dv=1.0,

    Pmax=2.0,

    omega0=omega0,

    power_controller=power_controller,

    voltage_controller=voltage_controller,

    tauE=0.05,

    Imax=2.0

)





# ==================================================
# Create load
# ==================================================


load = Load(

    name="Load1",

    P=1.5,

    Q=0.3

)





# ==================================================
# Connect components
# ==================================================


grid.add_device(

    sg,

    bus1

)



grid.add_device(

    gfm,

    bus2

)



grid.add_load(

    load,

    bus2

)





# ==================================================
# Initialise
# ==================================================


grid.initialise()



print("\n========================")

print("Grid states")

print("========================")



for name in grid.state_names:

    print(name)





print("\n========================")

print("Grid")

print("========================")


print(grid)





# ==================================================
# Initial state
# ==================================================


x0 = grid.initial_state()



print("\n========================")

print("Initial state")

print("========================")


print(x0)





# ==================================================
# Initial COI frequency
# ==================================================


omega_coi = grid.centre_of_inertia_frequency(

    x0

)



print("\n========================")

print("Initial COI frequency")

print("========================")


print(omega_coi)





# ==================================================
# Initial load
# ==================================================


print("\n========================")

print("Loads")

print("========================")


for l in grid.loads:

    print(l)





# ==================================================
# Simulation
# ==================================================


simulation = Simulation(

    grid

)



results = simulation.run(

    x0

)





# ==================================================
# Results
# ==================================================


print("\n========================")

print("Simulation complete")

print("========================")



print(results)





x_final = results.x[:,-1]





print("\n========================")

print("Final states")

print("========================")



for i,name in enumerate(grid.state_names):

    print(

        name,

        "=",

        x_final[i]

    )





# ==================================================
# Final COI
# ==================================================


omega_coi_final = grid.centre_of_inertia_frequency(

    x_final

)



print("\n========================")

print("Final COI frequency")

print("========================")


print(omega_coi_final)





# ==================================================
# Network voltages
# ==================================================


V,theta = grid.bus_measurements(

    x_final

)



print("\n========================")

print("Bus voltages")

print("========================")



for bus in grid.buses:

    print(

        bus.name,

        "V=",

        V[bus],

        "theta=",

        theta[bus]

    )





# ==================================================
# Line flows
# ==================================================


flows = grid.network.line_flows(

    V,

    theta

)



print("\n========================")

print("Line flows")

print("========================")



for l,p in flows.items():

    print(

        l,

        "P=",

        p

    )





# ==================================================
# Plotting
# ==================================================


try:


    plotter = Plotter(results)


    plotter.plot_states()


    plotter.plot_frequency_states()



except Exception as e:


    print(

        "Plotting failed:",

        e

    )