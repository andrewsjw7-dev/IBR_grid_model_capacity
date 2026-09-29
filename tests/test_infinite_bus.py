from models.infinite_bus import InfiniteBus


grid = InfiniteBus()


print("Voltage:")
print(grid.voltage_phasor())


delta = 0.5

Pe = grid.electrical_power(
    delta,
    Pmax=1.5
)


print()

print("Electrical power:")
print(Pe)