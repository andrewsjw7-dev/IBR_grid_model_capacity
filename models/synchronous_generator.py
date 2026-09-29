"""Classical synchronous generator behind transient reactance.

The physical terminal bus voltage is algebraic.  The generator internal EMF
is

    E' exp(j delta)

behind Xd'.  With absolute angular speed omega [rad/s], the preferred
conventional-inertia form is

    delta_dot = omega - omega0
    H_sys      = H Sr / S_base
    M_sys      = 2 H Sr / (omega0 S_base)
    omega_dot  = omega0/(2 H_sys)
                 * [Pm - Pe - D_sys (omega-omega0)/omega0].

For compatibility with the ESGI prototype, a legacy coefficient ``M`` may be
supplied instead of ``H``; then the old equation

    M omega_dot = Pm - Pe - D (omega-omega0)

is retained.  New work should use ``H``.
"""

import numpy as np
from models.device import Device


class SynchronousGenerator(Device):
    def __init__(
        self,
        name,
        M=None,
        D=0.0,
        Pm=0.0,
        Pmax=None,
        omega0=2 * np.pi * 50.0,
        H=None,
        E_internal=1.0,
        Xd_prime=None,
        Sr=1.0,
        S_base=1.0,
    ):
        if H is None and M is None:
            raise ValueError("Supply H (preferred) or legacy M.")
        if Xd_prime is None:
            if Pmax is None or Pmax <= 0:
                raise ValueError("Supply Xd_prime, or a positive legacy Pmax.")
            Xd_prime = E_internal / Pmax  # nominal V=1 compatibility

        self.Sr = float(Sr)
        self.S_base = float(S_base)
        if self.Sr <= 0.0 or self.S_base <= 0.0:
            raise ValueError("Sr and S_base must be positive.")
        self.rating_pu = self.Sr / self.S_base
        self.H = None if H is None else float(H)
        self.M = None if M is None else float(M)
        self.D_device = float(D)
        self.D = self.D_device * self.rating_pu if self.H is not None else self.D_device
        self.Pm = float(Pm)
        self.Pmax = Pmax
        self.omega0 = float(omega0)
        self.E_internal = float(E_internal)
        self.Xd_prime_device = float(Xd_prime)
        self.Xd_prime = self.Xd_prime_device / self.rating_pu
        self.H_system = None if self.H is None else self.H * self.rating_pu
        inertia_weight = self.H_system if self.H_system is not None else 0.5 * self.M * self.omega0
        super().__init__(name=name, inertia=inertia_weight)
        self.device_type = "voltage_source_behind_reactance"
        self.state_names = ["delta", "omega"]

    def initial_state(self):
        return np.array([0.0, self.omega0])

    def angle(self, x):
        return x[0]

    def frequency(self, x):
        return x[1]

    def voltage(self, x):
        return self.E_internal

    def internal_voltage(self, x):
        return self.E_internal * np.exp(1j * x[0])

    def current_injection(self, Vbus, x):
        return (self.internal_voltage(x) - Vbus) / (1j * self.Xd_prime)

    def terminal_power(self, Vbus, x):
        I = self.current_injection(Vbus, x)
        return Vbus * np.conj(I)

    def mechanical_power(self, t):
        """Override in subclasses to implement mechanical-power events."""
        return self.Pm

    def derivatives(self, t, x, electrical_inputs=None):
        delta, omega = x
        electrical_inputs = {} if electrical_inputs is None else electrical_inputs
        if "P" in electrical_inputs:
            Pe = electrical_inputs["P"]
        elif "V_complex" in electrical_inputs:
            Pe = self.terminal_power(electrical_inputs["V_complex"], x).real
        elif self.Pmax is not None:
            Pe = self.Pmax * np.sin(delta)
        else:
            raise ValueError("Electrical power is unavailable.")

        ddelta = omega - self.omega0
        Pm = self.mechanical_power(t)
        if self.H is not None:
            speed_dev_pu = (omega - self.omega0) / self.omega0
            domega = self.omega0 / (2 * self.H_system) * (
                Pm - Pe - self.D * speed_dev_pu
            )
        else:
            domega = (Pm - Pe - self.D * (omega - self.omega0)) / self.M
        return np.array([ddelta, domega])
