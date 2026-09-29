import numpy as np

from models.network import Network


network = Network()


delta = 0.5

Pe = network.electrical_power(

    delta,

    Pmax=1.5

)


print("Electrical power:")

print(Pe)