import numpy as np

from controls.droop import DroopController



omega0 = 2*np.pi*50



droop = DroopController(

    P0=0.8,

    kp=20,

    omega0=omega0

)



# Nominal frequency

P1 = droop.output(

    {
        "omega": omega0
    }

)



# Frequency drop of 0.1 rad/s

P2 = droop.output(

    {
        "omega": omega0-0.1
    }

)



print("Nominal power:")
print(P1)


print()

print("Power after frequency drop:")
print(P2)