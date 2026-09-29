"""Dynamic grid container with algebraic AC bus-voltage coupling.

The global differential state contains only device states.  At every RHS
call, bus phasors are obtained from the nonlinear algebraic KCL equations,
so the model is a semi-explicit index-1 DAE reduced by algebraic solution:

    xdot = f(x, z)
    0    = g(x, z),       z = bus-voltage phasors.

This preserves the original ESGI ``solve_ivp`` workflow while replacing the
prototype rule in which the first device on a bus imposed the bus voltage.
"""

import numpy as np
from models.dynamic_model import DynamicModel
from models.network import Network


class Grid(DynamicModel):
    def __init__(self, S_base=1.0):
        super().__init__()
        self.S_base = float(S_base)
        if self.S_base <= 0.0:
            raise ValueError("S_base must be positive.")
        self.buses = []
        self.lines = []
        self.loads = []
        self.devices = []
        self.infinite_buses = []
        self.device_bus = {}
        self.infinite_bus_bus = {}
        self.device_state_indices = {}
        self.network = None
        self.state_names = []
        self.n_states = 0
        self._voltage_guess = None
        self.last_bus_voltages = None

    # ------------------------------------------------------------------
    # Topology
    # ------------------------------------------------------------------
    def add_bus(self, bus):
        self.buses.append(bus)

    def add_line(self, line):
        self.lines.append(line)

    def update_network(self):
        self.network = Network(self.buses, self.lines)
        # Preserve the latest voltage solution only if all buses still exist.
        if self._voltage_guess is not None:
            self._voltage_guess = {
                bus: value for bus, value in self._voltage_guess.items()
                if bus in self.buses
            }

    # ------------------------------------------------------------------
    # Components
    # ------------------------------------------------------------------
    def add_load(self, load, bus):
        self.loads.append(load)
        load.connect_to_bus(bus)
        bus.add_load(load)

    def add_device(self, device, bus):
        device_base = getattr(device, "S_base", self.S_base)
        if abs(float(device_base) - self.S_base) > 1e-12:
            raise ValueError(
                f"Device {device.name} uses S_base={device_base}, "
                f"but Grid uses S_base={self.S_base}."
            )
        self.devices.append(device)
        self.device_bus[device] = bus
        bus.add_device(device)
        device.connect_to_bus(bus)

    def add_infinite_bus(self, infinite_bus, bus):
        self.infinite_buses.append(infinite_bus)
        self.infinite_bus_bus[infinite_bus] = bus
        infinite_bus.connect_to_bus(bus)

    # ------------------------------------------------------------------
    # State assembly
    # ------------------------------------------------------------------
    def initialise(self):
        self.state_names = []
        self.device_state_indices = {}
        index = 0
        for device in self.devices:
            n = len(device.state_names)
            self.device_state_indices[device] = slice(index, index + n)
            self.state_names.extend(f"{device.name}_{s}" for s in device.state_names)
            index += n
        self.n_states = index
        self.update_network()

    def initial_state(self):
        if self.network is None:
            self.initialise()
        x0 = []
        for device in self.devices:
            x0.extend(device.initial_state())
        return np.asarray(x0, dtype=float)

    def get_device_state(self, x, device):
        return x[self.device_state_indices[device]]

    # ------------------------------------------------------------------
    # Algebraic network equations
    # ------------------------------------------------------------------
    def fixed_bus_voltages(self):
        fixed = {}
        for source in self.infinite_buses:
            bus = self.infinite_bus_bus[source]
            V = source.voltage_phasor()
            if bus in fixed and abs(fixed[bus] - V) > 1e-12:
                raise ValueError(f"Conflicting ideal voltage sources on {bus}.")
            fixed[bus] = V
        return fixed

    def _load_current(self, bus, Vbus):
        """Current drawn by constant-PQ loads at ``bus`` (positive out of bus)."""
        if not bus.loads:
            return 0.0 + 0.0j
        if abs(Vbus) < 1e-8:
            raise RuntimeError(f"PQ load current is singular at low voltage on {bus}.")
        S = sum((load.P + 1j * load.Q) for load in bus.loads)
        return np.conj(S / Vbus)

    def _device_current(self, device, Vbus, x):
        state = self.get_device_state(x, device)
        if not hasattr(device, "current_injection"):
            raise TypeError(
                f"{device.__class__.__name__} has no current_injection() interface."
            )
        return device.current_injection(Vbus, state)

    def algebraic_solution(self, x):
        if self.network is None:
            self.initialise()

        fixed = self.fixed_bus_voltages()

        def component_current(bus, Vbus):
            I = 0.0 + 0.0j
            for device in bus.devices:
                I += self._device_current(device, Vbus, x)
            I -= self._load_current(bus, Vbus)
            return I

        V = self.network.solve_bus_voltages(
            current_injection=component_current,
            fixed_voltages=fixed,
            initial_guess=self._voltage_guess,
        )
        self._voltage_guess = dict(V)
        self.last_bus_voltages = dict(V)
        return V

    def bus_measurements(self, x):
        """Compatibility wrapper returning magnitude and angle dictionaries."""
        Vc = self.algebraic_solution(x)
        V = {bus: abs(v) for bus, v in Vc.items()}
        theta = {bus: np.angle(v) for bus, v in Vc.items()}
        return V, theta

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------
    def load_power(self):
        Pload = {bus: 0.0 for bus in self.buses}
        Qload = {bus: 0.0 for bus in self.buses}
        for load in self.loads:
            Pload[load.bus] += load.active_power()
            Qload[load.bus] += load.reactive_power()
        return Pload, Qload

    def centre_of_inertia_frequency(self, x):
        numerator = 0.0
        denominator = 0.0
        for device in self.devices:
            weight = getattr(device, "inertia", 0.0)
            if weight <= 0.0:
                continue
            state = self.get_device_state(x, device)
            numerator += weight * device.frequency(state)
            denominator += weight
        if denominator == 0.0:
            return 0.0
        return numerator / denominator

    def device_electrical_inputs(self, x, device, Vbus):
        state = self.get_device_state(x, device)
        I = device.current_injection(Vbus, state)
        S = Vbus * np.conj(I)
        return {
            "P": S.real,
            "Q": S.imag,
            "V": abs(Vbus),
            "theta": np.angle(Vbus),
            "V_complex": Vbus,
            "I_complex": I,
            "omega_coi": self.centre_of_inertia_frequency(x),
        }

    def power_balance_residual(self, x):
        """Return complex KCL residuals for diagnostics at all non-fixed buses."""
        Vdict = self.algebraic_solution(x)
        Vvec = np.array([Vdict[b] for b in self.buses], dtype=complex)
        Inet = self.network.Ybus @ Vvec
        fixed = self.fixed_bus_voltages()
        residual = {}
        for bus in self.buses:
            idx = self.network.bus_index[bus]
            Icomp = sum(
                self._device_current(device, Vdict[bus], x)
                for device in bus.devices
            ) - self._load_current(bus, Vdict[bus])
            residual[bus] = None if bus in fixed else Icomp - Inet[idx]
        return residual

    def device_powers(self, x, voltages=None):
        """Return terminal complex power for every dynamic device."""
        if voltages is None:
            voltages = self.algebraic_solution(x)
        powers = {}
        for device in self.devices:
            bus = self.device_bus[device]
            state = self.get_device_state(x, device)
            I = device.current_injection(voltages[bus], state)
            powers[device] = voltages[bus] * np.conj(I)
        return powers

    def line_reactive_absorption(self, voltages):
        """Reactive power absorbed by the lossless series reactances."""
        total = 0.0
        by_line = {}
        for line in self.lines:
            if not line.in_service:
                continue
            I = (voltages[line.from_bus] - voltages[line.to_bus]) / (1j * line.X)
            q = line.X * abs(I) ** 2
            by_line[line] = q
            total += q
        return total, by_line

    def operating_point_diagnostics(self, x):
        """Power-balance and residual diagnostics for a candidate equilibrium."""
        V = self.algebraic_solution(x)
        powers = self.device_powers(x, V)
        Pload = sum(float(load.active_power()) for load in self.loads)
        Qload = sum(float(load.reactive_power()) for load in self.loads)
        Pgen = sum(S.real for S in powers.values())
        Qgen = sum(S.imag for S in powers.values())
        q_lines, q_by_line = self.line_reactive_absorption(V)
        kcl = self.power_balance_residual(x)
        kcl_values = [abs(r) for r in kcl.values() if r is not None]
        rhs = self.derivatives(0.0, x)
        return {
            "bus_voltages": V,
            "device_powers": powers,
            "P_generation": float(Pgen),
            "Q_generation": float(Qgen),
            "P_load": float(Pload),
            "Q_load": float(Qload),
            "active_power_balance": float(Pgen - Pload),
            "reactive_network_absorption": float(q_lines),
            "reactive_balance_residual": float(Qgen - Qload - q_lines),
            "line_reactive_absorption": q_by_line,
            "max_kcl_residual": float(max(kcl_values, default=0.0)),
            "max_differential_residual": float(np.linalg.norm(rhs, ord=np.inf)),
        }

    # ------------------------------------------------------------------
    # Differential equations
    # ------------------------------------------------------------------
    def derivatives(self, t, x, electrical_inputs=None):
        dx = np.zeros_like(x, dtype=float)
        V = self.algebraic_solution(x)
        for device in self.devices:
            state = self.get_device_state(x, device)
            bus = self.device_bus[device]
            inputs = self.device_electrical_inputs(x, device, V[bus])
            dx_device = device.derivatives(t, state, inputs)
            dx[self.device_state_indices[device]] = dx_device
        return dx

    def __repr__(self):
        return (
            f"Grid({len(self.buses)} buses, {len(self.lines)} lines, "
            f"{len(self.devices)} devices, {len(self.loads)} loads, "
            f"{len(self.infinite_buses)} infinite buses)"
        )
