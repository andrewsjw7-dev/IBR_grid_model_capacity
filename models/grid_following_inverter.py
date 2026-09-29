"""Reduced grid-following inverter with SRF-PLL and ideal PQ current control.

States
------
theta : PLL phase estimate in the synchronous reference frame [rad]
xi    : integral state of the SRF-PLL phase detector

The bus voltage is *measured*, never imposed by the GFL.  With

    v_q = |V| sin(theta_grid - theta)

we use

    xi_dot    = v_q
    omega_hat = omega0 + Kp_pll v_q + Ki_pll xi
    theta_dot = omega_hat - omega0.

The converter injects the current corresponding to its commanded complex
power, subject to the radial current limit:

    I* = (Pref - j Qref) / conj(Vbus),   |I| <= Imax.
"""

import numpy as np
from models.device import Device
from controls.current_limiter import CurrentLimiter


class GridFollowingInverter(Device):
    def __init__(
        self,
        name,
        Pref,
        Qref,
        Kpll=None,
        Dpll=None,
        omega0=2 * np.pi * 50.0,
        V0=1.0,
        Imax=2.0,
        Kp_pll=None,
        Ki_pll=None,
        Sr=1.0,
        S_base=1.0,
    ):
        super().__init__(name=name, inertia=0.0)
        self.Sr = float(Sr)
        self.S_base = float(S_base)
        if self.Sr <= 0.0 or self.S_base <= 0.0:
            raise ValueError("Sr and S_base must be positive.")
        self.rating_pu = self.Sr / self.S_base
        self.Pref = float(Pref)
        self.Qref = float(Qref)
        # Backward-compatible argument positions.  In the corrected PI PLL,
        # Kpll/Dpll are interpreted as Kp/Ki if the explicit names are absent.
        self.Kp_pll = float(Kp_pll if Kp_pll is not None else (Kpll if Kpll is not None else 20.0))
        self.Ki_pll = float(Ki_pll if Ki_pll is not None else (Dpll if Dpll is not None else 200.0))
        self.Kpll = self.Kp_pll
        self.Dpll = self.Ki_pll
        self.omega0 = float(omega0)
        self.V0 = float(V0)
        self.Imax_device = float(Imax)
        self.Imax = self.Imax_device * self.rating_pu
        self.current_limiter = CurrentLimiter(self.Imax)
        self.device_type = "current_source"
        self.state_names = ["theta", "xi"]

    def initial_state(self):
        return np.array([0.0, 0.0])

    def angle(self, x):
        return x[0]

    def frequency(self, x):
        # At lock v_q=0.  For exact instantaneous PLL frequency use
        # pll_frequency(...), which also needs the measured bus voltage.
        return self.omega0 + self.Ki_pll * x[1]

    def voltage(self, x):
        # Compatibility only: a GFL never sets the bus voltage in Grid.
        return self.V0

    def phase_detector(self, Vbus, x):
        theta_grid = np.angle(Vbus)
        return abs(Vbus) * np.sin(theta_grid - x[0])

    def pll_frequency(self, Vbus, x):
        vq = self.phase_detector(Vbus, x)
        return self.omega0 + self.Kp_pll * vq + self.Ki_pll * x[1]

    def unconstrained_current(self, Vbus, x=None):
        if abs(Vbus) < 1e-8:
            raise RuntimeError("GFL current command is singular at near-zero bus voltage.")
        return (self.Pref - 1j * self.Qref) / np.conj(Vbus)

    def current_injection(self, Vbus, x):
        return self.current_limiter.limit(self.unconstrained_current(Vbus, x))

    def terminal_power(self, Vbus, x):
        I = self.current_injection(Vbus, x)
        return Vbus * np.conj(I)

    def derivatives(self, t, x, electrical_inputs=None):
        electrical_inputs = {} if electrical_inputs is None else electrical_inputs
        if "V_complex" in electrical_inputs:
            Vbus = electrical_inputs["V_complex"]
        else:
            Vmag = electrical_inputs.get("V", self.V0)
            theta_grid = electrical_inputs.get("theta", 0.0)
            Vbus = Vmag * np.exp(1j * theta_grid)
        vq = self.phase_detector(Vbus, x)
        xi = x[1]
        omega_hat = self.omega0 + self.Kp_pll * vq + self.Ki_pll * xi
        dtheta = omega_hat - self.omega0
        dxi = vq
        return np.array([dtheta, dxi])

    def active_power_reference(self):
        return self.Pref

    def reactive_power_reference(self):
        return self.Qref

    def __repr__(self):
        return f"GridFollowingInverter({self.name}, Pref={self.Pref}, Qref={self.Qref})"
