"""
test_smib.py

Single Machine Infinite Bus (SMIB)

SG -------- Infinite Bus

The infinite bus is represented by a very stiff
Grid Forming Inverter.

A line trip is applied at t = 20 s.
"""

import numpy as np

from models.grid import Grid
from models.bus import Bus
from models.line import Line
from models.load import Load

from models.synchronous_generator import SynchronousGenerator
from models.grid_forming_inverter import GridFormingInverter

from controls.droop import DroopController
from controls.voltage_droop import VoltageDroopController

from simulation.solver import Simulation

from disturbances.line_trip import LineTrip


# =====================================================
# Constants
# =====================================================

omega0 = 2*np.pi*50.0


# =====================================================
# Grid
# =====================================================

grid = Grid()


# =====================================================
# Buses
# =====================================================

bus1 = Bus("Generator")
bus2 = Bus("InfiniteBus")

grid.add_bus(bus1)
grid.add_bus(bus2)


# =====================================================
# Line
# =====================================================

line = Line(
    bus1,
    bus2,
    reactance=0.3
)

grid.add_line(line)


# =====================================================
# Load
# =====================================================

load = Load(
    "Load1",
    P=0.8,
    Q=0.2
)

grid.add_load(
    load,
    bus1
)


# =====================================================
# Synchronous Generator
# =====================================================

sg = SynchronousGenerator(

    name="SG1",

    M=5.0,

    D=1.0,

    Pm=1.0,

    Pmax=5.0,

    omega0=omega0

)

grid.add_device(
    sg,
    bus1
)


# =====================================================
# Infinite Bus
#
# Represented as a very stiff GFM
# =====================================================

power_controller = DroopController(

    P0=0.0,

    kp=0.0,

    omega0=omega0

)

voltage_controller = VoltageDroopController(

    V0=1.0,

    Q0=0.0,

    kq=0.0

)

infinite_bus = GridFormingInverter(

    name="InfiniteBus",

    Mv=1e6,

    Dv=1e6,

    Pmax=1000.0,

    omega0=omega0,

    power_controller=power_controller,

    voltage_controller=voltage_controller,

    tauE=0.001

)

grid.add_device(
    infinite_bus,
    bus2
)


# =====================================================
# Finalise Grid
# =====================================================

grid.initialise()

print()
print("="*60)
print("SMIB GRID")
print("="*60)
print(grid)

print()

print("State names")

for name in grid.state_names:
    print(name)


# =====================================================
# Initial State
# =====================================================

x0 = grid.initial_state()

print()
print("Initial state")
print(x0)

print()
print("Initial COI frequency")
print(grid.centre_of_inertia_frequency(x0))


# =====================================================
# Disturbance
# =====================================================

trip = LineTrip(

    line=line,

    trip_time=20.0

)


# =====================================================
# Simulation
# =====================================================

simulation = Simulation(

    model=grid,

    t_start=0.0,

    t_end=40.0,

    n_points=4000

)

simulation.add_disturbance(trip)

results = simulation.run(x0)


# =====================================================
# Results
# =====================================================

print()

print("="*60)
print("FINAL STATES")
print("="*60)

for i, name in enumerate(grid.state_names):

    print(f"{name:20s} {results.x[i,-1]:12.6f}")

print()

print("Final COI frequency")

print(

    grid.centre_of_inertia_frequency(

        results.x[:,-1]

    )

)

print()

print("Line status")

print(

    line,

    "in service =",

    line.in_service

)


# =====================================================
# Plot
# =====================================================

try:

    from simulation.plotter import Plotter

    Plotter().plot(results)

except Exception as e:

    print()

    print("Plot skipped:", e)


print()

print("SMIB test complete")