"""Electrical network and algebraic bus-voltage solver.

The network uses the standard current-injection convention

    I_net = Ybus V
    S_net = V * conj(I_net)

so positive P/Q denote power injected from a bus into the transmission
network.  Dynamic devices and loads are coupled in :mod:`models.grid`
through Kirchhoff current balance.
"""

import numpy as np
from scipy.optimize import root


class Network:
    def __init__(self, buses, lines):
        self.buses = list(buses)
        self.lines = list(lines)
        self.bus_index = {bus: i for i, bus in enumerate(self.buses)}
        self.nbus = len(self.buses)
        self.Ybus = self.build_ybus()

    def build_ybus(self):
        Y = np.zeros((self.nbus, self.nbus), dtype=complex)
        for line in self.lines:
            if not line.in_service:
                continue
            if line.X == 0:
                raise ValueError("Line reactance must be non-zero.")
            i = self.bus_index[line.from_bus]
            j = self.bus_index[line.to_bus]
            y = 1.0 / (1j * line.X)
            Y[i, i] += y
            Y[j, j] += y
            Y[i, j] -= y
            Y[j, i] -= y
        return Y

    def update(self):
        self.Ybus = self.build_ybus()

    def voltage_vector(self, magnitude, angle):
        V = np.zeros(self.nbus, dtype=complex)
        for bus in self.buses:
            i = self.bus_index[bus]
            V[i] = magnitude[bus] * np.exp(1j * angle[bus])
        return V

    def power_injections(self, magnitude, angle):
        """Return transmission-network injections using S = V conj(YV)."""
        V = self.voltage_vector(magnitude, angle)
        I = self.Ybus @ V
        S = V * np.conj(I)
        P = {bus: S[self.bus_index[bus]].real for bus in self.buses}
        Q = {bus: S[self.bus_index[bus]].imag for bus in self.buses}
        return P, Q

    def active_power(self, voltage, angle):
        return self.power_injections(voltage, angle)[0]

    def reactive_power(self, voltage, angle):
        return self.power_injections(voltage, angle)[1]

    def line_flows(self, voltage, angle):
        flows = {}
        for line in self.lines:
            if not line.in_service:
                continue
            Vi = voltage[line.from_bus]
            Vj = voltage[line.to_bus]
            ti = angle[line.from_bus]
            tj = angle[line.to_bus]
            flows[line] = Vi * Vj / line.X * np.sin(ti - tj)
        return flows

    def solve_bus_voltages(
        self,
        current_injection,
        fixed_voltages=None,
        initial_guess=None,
        tol=1e-10,
    ):
        """Solve the algebraic KCL equations for bus voltages.

        Parameters
        ----------
        current_injection : callable
            ``current_injection(bus, Vbus)`` returns the net component
            current injected *into* the bus (generation minus load).  It may
            depend nonlinearly on the local voltage.
        fixed_voltages : dict, optional
            Mapping ``bus -> complex voltage`` for ideal/infinite buses.
        initial_guess : dict, optional
            Mapping ``bus -> complex voltage`` used to initialise the root
            solve for non-fixed buses.

        Notes
        -----
        For every non-fixed bus i the residual is

            0 = I_components,i(V_i) - (Ybus V)_i.

        Fixed buses impose their voltage exactly; their residual current is
        supplied/absorbed by the ideal source.
        """
        fixed_voltages = {} if fixed_voltages is None else dict(fixed_voltages)
        unknown = [bus for bus in self.buses if bus not in fixed_voltages]

        if not unknown:
            return dict(fixed_voltages)

        def unpack(y):
            V = np.zeros(self.nbus, dtype=complex)
            for bus, value in fixed_voltages.items():
                V[self.bus_index[bus]] = value
            n = len(unknown)
            for k, bus in enumerate(unknown):
                V[self.bus_index[bus]] = y[k] + 1j * y[n + k]
            return V

        y0 = np.zeros(2 * len(unknown))
        for k, bus in enumerate(unknown):
            guess = 1.0 + 0.0j
            if initial_guess is not None and bus in initial_guess:
                guess = complex(initial_guess[bus])
            y0[k] = guess.real
            y0[len(unknown) + k] = guess.imag

        def residual(y):
            V = unpack(y)
            Inet = self.Ybus @ V
            r = np.zeros(len(unknown), dtype=complex)
            for k, bus in enumerate(unknown):
                idx = self.bus_index[bus]
                r[k] = current_injection(bus, V[idx]) - Inet[idx]
            return np.concatenate((r.real, r.imag))

        sol = root(residual, y0, method="hybr", tol=tol)
        rnorm = np.linalg.norm(residual(sol.x), ord=np.inf)
        if rnorm > max(1e-8, 100 * tol):
            # A flat restart makes failure messages less sensitive to an old
            # warm start after a large switching event.
            flat = np.concatenate((np.ones(len(unknown)), np.zeros(len(unknown))))
            sol2 = root(residual, flat, method="hybr", tol=tol)
            rnorm2 = np.linalg.norm(residual(sol2.x), ord=np.inf)
            if sol2.success and rnorm2 < rnorm:
                sol, rnorm = sol2, rnorm2

        if rnorm > max(1e-8, 100 * tol):
            raise RuntimeError(
                "Algebraic network solve failed: "
                f"{sol.message}; residual_inf={rnorm:.3e}"
            )

        V = unpack(sol.x)
        return {bus: V[self.bus_index[bus]] for bus in self.buses}
