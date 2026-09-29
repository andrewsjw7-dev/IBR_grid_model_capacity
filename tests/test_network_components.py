from models.bus import Bus
from models.line import Line



bus1 = Bus(

    "Bus 1",

    voltage=1.0,

    angle=0.2

)



bus2 = Bus(

    "Bus 2",

    voltage=1.0,

    angle=0.0

)



line = Line(

    bus1,

    bus2,

    reactance=0.2

)



print(bus1)

print(bus2)

print(line)



print(

    "Power flow:",

    line.power_flow()

)