"""
Mixed SG + GFM network test.

Purpose:

1. Test SG and GFM models together.

2. Calculate centre of inertia frequency:

              sum(M_i omega_i)
    omegaCOI = -----------------
                 sum(M_i)


System:

                 Network

          +----------------+

          |                |

          v                v


         SG               GFM


          |                |

          +----------------+


                 |
             Infinite Bus


"""


import numpy as np
import matplotlib.pyplot as plt


from models.network import Network

from models.synchronous_generator import SynchronousGenerator

from models.grid_forming_inverter import GridFormingInverter


from controls.droop import DroopController

from controls.voltage_droop import VoltageDroopController


from simulation.solver import Simulation





# ==================================================
# Grid parameters
# ==================================================

F0 = 50.0

OMEGA0 = 2*np.pi*F0





# ==================================================
# Create network
# ==================================================

network = Network()





# ==================================================
# Synchronous generator
# ==================================================

M_SG = 8.0


sg = SynchronousGenerator(

    M=M_SG,

    D=1.5,

    Pm=0.8,

    Pmax=1.5,

    omega0=OMEGA0,

    network=network

)





# ==================================================
# Grid-forming inverter controllers
# ==================================================

power_controller = DroopController(

    P0=0.4+0.2,

    kp=20,

    omega0=OMEGA0

)



voltage_controller = VoltageDroopController(

    V0=1.0,

    Q0=0.0,

    kq=0.05

)





# ==================================================
# Grid-forming inverter
# ==================================================

M_GFM = 2.0


gfm = GridFormingInverter(

    Mv=M_GFM,

    Dv=1.0,

    Pmax=1.0,

    omega0=OMEGA0,

    power_controller=power_controller,

    voltage_controller=voltage_controller,

    network=network,

    tauE=0.05

)





# ==================================================
# Initial conditions
# ==================================================

# SG equilibrium

delta_sg = np.arcsin(

    0.8 / 1.5

)


x0_sg = [

    delta_sg,

    OMEGA0

]




# GFM equilibrium

delta_gfm = np.arcsin(

    0.4 / 1.0

)


x0_gfm = [

    delta_gfm,

    OMEGA0,

    1.0

]





# ==================================================
# Simulate SG
# ==================================================

simulation_sg = Simulation(

    model=sg,

    t_start=0.0,

    t_end=20.0,

    n_points=4000

)


simulation_sg.summary()



results_sg = simulation_sg.run(

    x0_sg

)





# ==================================================
# Simulate GFM
# ==================================================

simulation_gfm = Simulation(

    model=gfm,

    t_start=0.0,

    t_end=20.0,

    n_points=4000

)


simulation_gfm.summary()



results_gfm = simulation_gfm.run(

    x0_gfm

)





# ==================================================
# Extract frequency states
# ==================================================

# State ordering:
#
# SG:
#
# x[0] = delta
# x[1] = omega
#
#
# GFM:
#
# x[0] = delta
# x[1] = omega
# x[2] = E



omega_sg = results_sg.x[1, :]


omega_gfm = results_gfm.x[1, :]



time = results_sg.t





# ==================================================
# Calculate COI frequency
# ==================================================

omega_coi = (

    M_SG * omega_sg

    +

    M_GFM * omega_gfm

) / (

    M_SG + M_GFM

)



frequency_sg = omega_sg/(2*np.pi)

frequency_gfm = omega_gfm/(2*np.pi)

frequency_coi = omega_coi/(2*np.pi)





# ==================================================
# Print validation
# ==================================================

print()

print("--------------------------------")

print("COI Validation")

print("--------------------------------")


print(

    "Initial COI frequency:",

    frequency_coi[0],

    "Hz"

)


print(

    "Final COI frequency:",

    frequency_coi[-1],

    "Hz"

)


print("--------------------------------")





# ==================================================
# Plot frequencies
# ==================================================

plt.figure(figsize=(9,5))


plt.plot(

    time,

    frequency_sg,

    label="Synchronous Generator"

)


plt.plot(

    time,

    frequency_gfm,

    label="Grid Forming Inverter"

)


plt.plot(

    time,

    frequency_coi,

    linewidth=3,

    label="Centre of Inertia"

)



plt.xlabel("Time (s)")


plt.ylabel("Frequency (Hz)")


plt.title(

    "SG + GFM Frequency Response and COI"

)


plt.grid(True)


plt.legend()


plt.show()