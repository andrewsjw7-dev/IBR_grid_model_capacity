"""
test_sg_gfm.py

SG-GFM transient stability test with line trip.

Network:

          SG1
           |
          Bus1 -------- Bus2
                         |
                        GFM1
                         |
                       Load1


Experiment
-----------

0 - 25 s:
    Normal operation

t = 25 s:
    Transmission line trip

25 - 60 s:
    Post-disturbance response


Purpose
-------
Test:

    - SG model
    - GFM model
    - load model
    - network topology
    - disturbance framework
    - line trip event
    - COI frequency response
"""


import numpy as np
import matplotlib.pyplot as plt


# -----------------------------------------------------
# Models
# -----------------------------------------------------

from models.bus import Bus
from models.line import Line
from models.load import Load
from models.grid import Grid

from models.synchronous_generator import SynchronousGenerator
from models.grid_forming_inverter import GridFormingInverter


# -----------------------------------------------------
# Controllers
# -----------------------------------------------------

from controls.droop import DroopController
from controls.voltage_droop import VoltageDroopController


# -----------------------------------------------------
# Simulation
# -----------------------------------------------------

from simulation.solver import Simulation


# -----------------------------------------------------
# Disturbances
# -----------------------------------------------------

from disturbances.line_trip import LineTrip



# =====================================================
# Constants
# =====================================================

omega0 = 2*np.pi*50



# =====================================================
# Create grid
# =====================================================

grid = Grid()



bus1 = Bus(
    "Bus1"
)


bus2 = Bus(
    "Bus2"
)



grid.add_bus(bus1)

grid.add_bus(bus2)



# -----------------------------------------------------
# Transmission line
# -----------------------------------------------------

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
# Connect components
# =====================================================


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



# =====================================================
# Initialise grid
# =====================================================


grid.initialise()



print("\n"+"="*60)

print("GRID SUMMARY")

print("="*60)

print(grid)



# =====================================================
# Initial state
# =====================================================


x0 = grid.initial_state()



print("\nInitial state")

print(x0)



print("\nState names")

for name in grid.state_names:

    print(name)



# =====================================================
# Initial frequency
# =====================================================


print("\nInitial COI frequency")

print(

    grid.centre_of_inertia_frequency(x0)

)



# =====================================================
# Disturbance
# =====================================================


line_trip = LineTrip(

    line=line,

    trip_time=25.0

)



# =====================================================
# Simulation
# =====================================================


simulation = Simulation(

    model=grid,

    disturbances=[

        line_trip

    ],

    t_start=0.0,

    t_end=26.0,

    n_points=6000,

    method="RK45"

)



simulation.summary()



results = simulation.run(x0)



# =====================================================
# Final states
# =====================================================


xf = results.x[:, -1]


print("\nFinal states")

for name,value in zip(

        grid.state_names,

        xf):

    print(

        f"{name:15s} {value:12.6f}"

    )



print("\nFinal COI frequency")

print(

    grid.centre_of_inertia_frequency(xf)

)



# =====================================================
# Line status
# =====================================================


print("\nLine status")

for l in grid.lines:

    print(

        l,

        "in service =",

        l.in_service

    )



# =====================================================
# Frequency plots
# =====================================================


t = results.t



omega_sg = results.x[1,:]

omega_gfm = results.x[3,:]



plt.figure(figsize=(9,4))


plt.plot(

    t,

    omega_sg - omega0

)


plt.plot(

    t,

    omega_gfm - omega0

)



plt.axvline(

    25.0,

    linestyle="--",

    label="Line trip"

)



plt.xlabel(

    "Time (s)"

)


plt.ylabel(

    "Frequency deviation (rad/s)"

)



plt.legend(

    [

        "SG",

        "GFM",

        "Trip"

    ]

)



plt.grid()

plt.title(

    "SG-GFM Frequency Response to Line Trip"

)



plt.show()



# =====================================================
# COI frequency plot
# =====================================================


coi = []


for k in range(results.x.shape[1]):

    coi.append(

        grid.centre_of_inertia_frequency(

            results.x[:,k]

        )

    )



plt.figure(figsize=(9,4))


plt.plot(

    t,

    np.array(coi)-omega0

)



plt.axvline(

    25.0,

    linestyle="--"

)



plt.xlabel(

    "Time (s)"

)


plt.ylabel(

    "COI frequency deviation (rad/s)"

)



plt.grid()

plt.title(

    "Centre of Inertia Frequency Response"

)



plt.show()



print("\nTest complete")