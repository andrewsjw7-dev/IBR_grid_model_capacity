"""Ideal infinite-bus voltage source."""

import numpy as np


class InfiniteBus:
    def __init__(self, voltage=1.0, angle=0.0, frequency=50.0, name="InfiniteBus"):
        self.name = name
        self.voltage = float(voltage)
        self.angle = float(angle)
        self.frequency = float(frequency)
        self.omega = 2 * np.pi * self.frequency
        self.bus = None

    def connect_to_bus(self, bus):
        self.bus = bus

    def voltage_phasor(self):
        return self.voltage * np.exp(1j * self.angle)

    def electrical_power(self, delta, Pmax):
        return Pmax * np.sin(delta - self.angle)

    def __repr__(self):
        return (
            f"InfiniteBus({self.name}, V={self.voltage}, "
            f"angle={self.angle}, f={self.frequency})"
        )
