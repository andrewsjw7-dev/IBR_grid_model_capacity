"""Reduced-order grid-forming inverter behind filter/virtual reactance."""

import numpy as np
from models.device import Device
from controls.current_limiter import CurrentLimiter


class GridFormingInverter(Device):
    def __init__(
        self,
        name,
        Mv=None,
        Dv=0.0,
        Pmax=None,
        omega0=2 * np.pi * 50.0,
        power_controller=None,
        voltage_controller=None,
        tauE=0.05,
        Imax=2.0,
        Hv=None,
        X_filter=None,
        Sr=1.0,
        S_base=1.0,
    ):
        if Hv is None and Mv is None:
            raise ValueError("Supply Hv (preferred) or legacy Mv.")
        if X_filter is None:
            if Pmax is None or Pmax <= 0:
                raise ValueError("Supply X_filter, or a positive legacy Pmax.")
            X_filter = 1.0 / Pmax
        if power_controller is None or voltage_controller is None:
            raise ValueError("GFM requires power and voltage controllers.")

        self.Sr = float(Sr)
        self.S_base = float(S_base)
        if self.Sr <= 0.0 or self.S_base <= 0.0:
            raise ValueError("Sr and S_base must be positive.")
        self.rating_pu = self.Sr / self.S_base
        self.Hv = None if Hv is None else float(Hv)
        self.Mv = None if Mv is None else float(Mv)
        self.Dv_device = float(Dv)
        self.Dv = self.Dv_device * self.rating_pu if self.Hv is not None else self.Dv_device
        self.Pmax = Pmax
        self.omega0 = float(omega0)
        self.power_controller = power_controller
        self.voltage_controller = voltage_controller
        self.tauE = float(tauE)
        self.Imax_device = float(Imax)
        self.Imax = self.Imax_device * self.rating_pu
        self.X_filter_device = float(X_filter)
        self.X_filter = self.X_filter_device / self.rating_pu
        self.current_limiter = CurrentLimiter(self.Imax)
        self.Hv_system = None if self.Hv is None else self.Hv * self.rating_pu
        inertia_weight = self.Hv_system if self.Hv_system is not None else 0.5 * self.Mv * self.omega0
        super().__init__(name=name, inertia=inertia_weight)
        self.device_type = "voltage_source_behind_reactance"
        self.state_names = ["delta", "omega", "E"]

    def initial_state(self):
        return np.array([0.0, self.omega0, 1.0])

    def angle(self, x):
        return x[0]

    def frequency(self, x):
        return x[1]

    def voltage(self, x):
        return x[2]

    def internal_voltage(self, x):
        return x[2] * np.exp(1j * x[0])

    def unconstrained_current(self, Vbus, x):
        return (self.internal_voltage(x) - Vbus) / (1j * self.X_filter)

    def current_injection(self, Vbus, x):
        return self.current_limiter.limit(self.unconstrained_current(Vbus, x))

    def terminal_power(self, Vbus, x):
        I = self.current_injection(Vbus, x)
        return Vbus * np.conj(I)

    def derivatives(self, t, x, electrical_inputs=None):
        delta, omega, E = x
        electrical_inputs = {} if electrical_inputs is None else electrical_inputs
        if "P" in electrical_inputs:
            Pe = electrical_inputs["P"]
        elif "V_complex" in electrical_inputs:
            Pe = self.terminal_power(electrical_inputs["V_complex"], x).real
        elif self.Pmax is not None:
            # Corrected sign relative to the ESGI prototype.
            Pe = self.Pmax * E * np.sin(delta)
        else:
            raise ValueError("Electrical power is unavailable.")
        Qe = electrical_inputs.get("Q", 0.0)
        Vbus = electrical_inputs.get("V", E)
        omega_coi = electrical_inputs.get("omega_coi", self.omega0)

        Pref = self.power_controller.output(
            {"omega": omega, "omega_coi": omega_coi, "P": Pe}
        )
        Eref = self.voltage_controller.output({"voltage": Vbus, "Q": Qe})

        ddelta = omega - self.omega0
        if self.Hv is not None:
            speed_dev_pu = (omega - self.omega0) / self.omega0
            domega = self.omega0 / (2 * self.Hv_system) * (
                Pref - Pe - self.Dv * speed_dev_pu
            )
        else:
            domega = (Pref - Pe - self.Dv * (omega - self.omega0)) / self.Mv
        dE = (Eref - E) / self.tauE
        return np.array([ddelta, domega, dE])
