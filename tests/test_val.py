"""
test_grid.py

Regression test for the transient stability framework.

Network:

        Bus1 ------------- Bus2
          |                  |
         SG1               GFM1
                             |
                           Load1
"""

import numpy as np

from models.bus import Bus
from models.line import Line
from models.load import Load
from models.grid import Grid

from models.synchronous_generator import SynchronousGenerator
from models.grid_forming_inverter import GridFormingInverter

from controls.droop import DroopController
from controls.voltage_droop import VoltageDroopController

from simulation.solver import Simulation
from simulation.plotter import Plotter


# =====================================================
# Constants
# =====================================================

omega0 = 2*np.pi*50


# =====================================================
# Build network
# =====================================================

grid = Grid()

bus1 = Bus("Bus1")
bus2 = Bus("Bus2")

grid.add_bus(bus1)
grid.add_bus(bus2)

line = Line(
    bus1,
    bus2,
    reactance=0.2
)

grid.add_line(line)


# =====================================================
# Controllers
# =====================================================

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


# =====================================================
# Devices
# =====================================================

sg = SynchronousGenerator(
    name="SG1",
    M=5.0,
    D=1.0,
    Pm=1.0,
    Pmax=2.0,
    omega0=omega0
)

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


# =====================================================
# Load
# =====================================================

load = Load(
    name="Load1",
    P=1.5,
    Q=0.2
)


# =====================================================
# Connect everything
# =====================================================

grid.add_device(sg, bus1)
grid.add_device(gfm, bus2)

grid.add_load(load, bus2)


# =====================================================
# Initialise grid
# =====================================================

grid.initialise()


# =====================================================
# Summary
# =====================================================

print("="*60)
print("GRID SUMMARY")
print("="*60)

print(grid)

print("\nBuses")
for bus in grid.buses:
    print(" ", bus)

print("\nLines")
for line in grid.lines:
    print(" ", line)

print("\nLoads")
for load in grid.loads:
    print(" ", load)

print("\nDevices")
for device in grid.devices:
    print(" ", device.name)


# =====================================================
# State vector
# =====================================================

x0 = grid.initial_state()

print("\nInitial state")
print(x0)

print("\nState names")

for name in grid.state_names:
    print(" ", name)


# =====================================================
# Initial COI
# =====================================================

omega_coi = grid.centre_of_inertia_frequency(x0)

print("\nInitial COI frequency")
print(omega_coi)


# =====================================================
# Simulation
# =====================================================

simulation = Simulation(

    model=grid,

    t_start=0.0,

    t_end=20.0,

    n_points=2000,

    method="RK45"

)

simulation.summary()

results = simulation.run(x0)


# =====================================================
# Results
# =====================================================

print("\n========================")
print("Simulation complete")
print("========================")

print(results)

xf = results.x[:, -1]


print("\n========================")
print("Final states")
print("========================")

for name, value in zip(grid.state_names, xf):

    print(f"{name:20s} = {value:12.6f}")


# =====================================================
# Final COI
# =====================================================

print("\n========================")
print("Final COI frequency")
print("========================")

print(
    grid.centre_of_inertia_frequency(xf)
)


# =====================================================
# Bus measurements
# =====================================================

V, theta = grid.bus_measurements(xf)

print("\n========================")
print("Bus Voltages")
print("========================")

for bus in grid.buses:

    print(
        f"{bus.name:8s} "
        f"V={V[bus]:8.4f} "
        f"theta={theta[bus]:10.6f}"
    )


# =====================================================
# Network injections
# =====================================================

try:

    P, Q = grid.network.power_injections(V, theta)

    print("\n========================")
    print("Bus Power Injections")
    print("========================")

    for bus in grid.buses:

        print(
            f"{bus.name:8s} "
            f"P={P[bus]:10.5f} "
            f"Q={Q[bus]:10.5f}"
        )

except AttributeError:

    print("\nNetwork power injections not yet implemented.")


# =====================================================
# Line flows
# =====================================================

print("\n========================")
print("Line Flows")
print("========================")

flows = grid.network.line_flows(V, theta)

for line, power in flows.items():

    print(
        f"{line}   P = {power:.6f}"
    )


# =====================================================
# Plotting
# =====================================================

try:

    plotter = Plotter(results)

    if hasattr(plotter, "plot_states"):
        plotter.plot_states()

    if hasattr(plotter, "plot_frequency_states"):
        plotter.plot_frequency_states()

except Exception as e:

    print("\nPlotting skipped:", e)


print("\n========================")
print("Test complete")
print("========================")