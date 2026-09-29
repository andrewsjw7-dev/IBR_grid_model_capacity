"""
test_sg_gfm_gfl.py

Three device benchmark:

        SG + GFM + GFL


Network:

        SG1
         |
        Bus1
         |
       Line12
         |
        Bus2
         |
       Line23
         |
        Bus3
       /    \
    GFL1    Load


Purpose:

    - Verify mixed device simulation
    - SG inertia response
    - GFM virtual inertia response
    - GFL PLL dynamics


"""


import numpy as np


# =====================================================
# Models
# =====================================================

from models.grid import Grid

from models.bus import Bus

from models.line import Line

from models.load import Load


from models.synchronous_generator import (
    SynchronousGenerator
)


from models.grid_forming_inverter import (
    GridFormingInverter
)


from models.grid_following_inverter import (
    GridFollowingInverter
)



# =====================================================
# Controls
# =====================================================

from controls.droop import DroopController

from controls.voltage_droop import (
    VoltageDroopController
)



# =====================================================
# Simulation
# =====================================================

from simulation.solver import Simulation





# =====================================================
# Parameters
# =====================================================

omega0 = 2*np.pi*50





# =====================================================
# Create grid
# =====================================================

grid = Grid()





# =====================================================
# Buses
# =====================================================

bus1 = Bus("Bus1")

bus2 = Bus("Bus2")

bus3 = Bus("Bus3")



grid.add_bus(bus1)

grid.add_bus(bus2)

grid.add_bus(bus3)





# =====================================================
# Transmission lines
# =====================================================

line12 = Line(

    bus1,

    bus2,

    reactance=0.15

)


line23 = Line(

    bus2,

    bus3,

    reactance=0.20

)



grid.add_line(line12)

grid.add_line(line23)





# =====================================================
# Load
# =====================================================

load = Load(

    name="Load1",

    P=1.2,

    Q=0.3

)


grid.add_load(

    load,

    bus3

)





# =====================================================
# Synchronous generator
# =====================================================

sg = SynchronousGenerator(

    name="SG1",

    M=5.0,

    D=1.0,

    Pm=1.0,

    Pmax=2.0,

    omega0=omega0

)


grid.add_device(

    sg,

    bus1

)





# =====================================================
# GFM controllers
# =====================================================

power_controller = DroopController(

    P0=0.8,

    kp=0.05,

    omega0=omega0

)



voltage_controller = VoltageDroopController(

    V0=1.0,

    Q0=0.0,

    kq=0.05

)





# =====================================================
# Grid forming inverter
# =====================================================

gfm = GridFormingInverter(

    name="GFM1",

    Mv=1.5,

    Dv=0.5,

    Pmax=1.5,

    omega0=omega0,

    power_controller=power_controller,

    voltage_controller=voltage_controller

)


grid.add_device(

    gfm,

    bus2

)





# =====================================================
# Grid following inverter
# =====================================================

gfl = GridFollowingInverter(

    name="GFL1",

    Pref=0.4,

    Qref=0.0,

    Kpll=50.0,

    Dpll=5.0,

    omega0=omega0

)



grid.add_device(

    gfl,

    bus3

)





# =====================================================
# Initialise
# =====================================================

grid.initialise()



print()

print("="*60)

print("GRID SUMMARY")

print("="*60)

print(grid)



print()

print("Devices")

for device in grid.devices:

    print(device.name)



print()

print("Loads")

for load in grid.loads:

    print(load)





# =====================================================
# Initial state
# =====================================================

x0 = grid.initial_state()



print()

print("Initial state")

print(x0)



print()

print("State names")

for name in grid.state_names:

    print(name)



print()

print("Initial COI frequency")

print(

    grid.centre_of_inertia_frequency(x0)

)





# =====================================================
# Simulation
# =====================================================

simulation = Simulation(

    grid,

    t_start=0.0,

    t_end=30.0,

    n_points=3000

)



simulation.summary()



results = simulation.run(x0)





# =====================================================
# Final results
# =====================================================

x_final = results.final_state()



print()

print("="*60)

print("FINAL STATES")

print("="*60)



for name,value in zip(

        grid.state_names,

        x_final):


    print(

        f"{name:20s} {value:12.6f}"

    )





print()

print("Final COI frequency")

print(

    grid.centre_of_inertia_frequency(

        x_final

    )

)





# =====================================================
# Line flows
# =====================================================

print()

print("Line flows")



try:

    V,theta = grid.bus_measurements(

        x_final

    )


    flows = grid.network.line_flows(

        V,

        theta

    )


    for line,P in flows.items():

        print(

            line,

            "P =",

            P

        )


except Exception as e:

    print(

        "Line flow calculation failed:",

        e

    )





# =====================================================
# Plot
# =====================================================

try:

    results.plot_states()


except Exception as e:

    print(

        "Plot skipped:",

        e

    )





print()

print("Test complete")