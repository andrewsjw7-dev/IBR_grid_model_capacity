"""Exact-equilibrium validation problems for the corrected DAE baseline.

Run from the repository root with

    python -m validation.baseline_validations

The three cases are intentionally small enough that their equilibria are
known analytically.  The numerical DAE reduction is checked both at the exact
equilibrium and after a small perturbation.
"""

import numpy as np

from controls.droop import DroopController
from controls.voltage_droop import VoltageDroopController
from models.bus import Bus
from models.grid import Grid
from models.grid_following_inverter import GridFollowingInverter
from models.grid_forming_inverter import GridFormingInverter
from models.infinite_bus import InfiniteBus
from models.line import Line
from models.synchronous_generator import SynchronousGenerator
from simulation.solver import Simulation


F0 = 50.0
OMEGA0 = 2 * np.pi * F0


def _series_terminal_voltage(Ephasor, Vinf, Xdevice, Xline):
    """Exact terminal voltage for two lossless series reactances."""
    I = (Ephasor - Vinf) / (1j * (Xdevice + Xline))
    Vterminal = Vinf + 1j * Xline * I
    return Vterminal, I


def validate_sg(verbose=True):
    """SG behind Xd' + line connected to an infinite bus."""
    E = 1.10
    Vinf = 1.0
    theta_inf = 0.0
    Xd = 0.30
    Xline = 0.40
    Pm = 0.80
    H = 5.0
    D = 12.0

    Xtot = Xd + Xline
    Pmax_exact = E * Vinf / Xtot
    delta_star = np.arcsin(Pm / Pmax_exact) + theta_inf
    Ephasor = E * np.exp(1j * delta_star)
    Vt_exact, I_exact = _series_terminal_voltage(
        Ephasor, Vinf * np.exp(1j * theta_inf), Xd, Xline
    )
    S_exact = Vt_exact * np.conj(I_exact)

    bsg, binf = Bus("SG_bus"), Bus("Infinite_bus")
    grid = Grid()
    grid.add_bus(bsg)
    grid.add_bus(binf)
    grid.add_line(Line(bsg, binf, Xline))
    grid.add_infinite_bus(InfiniteBus(Vinf, theta_inf, F0), binf)
    sg = SynchronousGenerator(
        name="SG",
        H=H,
        D=D,
        Pm=Pm,
        omega0=OMEGA0,
        E_internal=E,
        Xd_prime=Xd,
    )
    grid.add_device(sg, bsg)
    grid.initialise()

    xeq = np.array([delta_star, OMEGA0])
    Veq = grid.algebraic_solution(xeq)
    rhs_eq = grid.derivatives(0.0, xeq)
    S_num = sg.terminal_power(Veq[bsg], xeq)

    assert abs(Veq[bsg] - Vt_exact) < 1e-9
    assert abs(S_num - S_exact) < 1e-9
    assert abs(S_num.real - Pm) < 1e-9
    assert np.linalg.norm(rhs_eq, ord=np.inf) < 1e-8

    x0 = xeq.copy()
    x0[0] += 0.04
    result = Simulation(grid, t_end=12.0, n_points=1201, rtol=1e-9, atol=1e-11).run(x0)
    final = result.final_state()
    assert abs(final[0] - delta_star) < 2e-3
    assert abs(final[1] - OMEGA0) < 2e-3

    out = {
        "delta_star_rad": delta_star,
        "terminal_voltage": Veq[bsg],
        "P_terminal": S_num.real,
        "Q_terminal": S_num.imag,
        "equilibrium_rhs_inf": np.linalg.norm(rhs_eq, ord=np.inf),
        "final_delta_error": final[0] - delta_star,
        "final_frequency_error_hz": (final[1] - OMEGA0) / (2 * np.pi),
    }
    if verbose:
        print("SG infinite-bus validation: PASS")
        for k, v in out.items():
            print(f"  {k}: {v}")
    return out


def validate_gfm(verbose=True):
    """GFM behind filter reactance + line connected to an infinite bus."""
    E_star = 1.05
    Vinf = 1.0
    theta_inf = 0.0
    Xf = 0.15
    Xline = 0.35
    P0 = 0.70
    Hv = 2.5
    Dv = 8.0
    kp = 0.15  # pu power per rad/s
    kq = 0.08
    tauE = 0.08

    Xtot = Xf + Xline
    Pmax_exact = E_star * Vinf / Xtot
    delta_star = np.arcsin(P0 / Pmax_exact) + theta_inf
    Ephasor = E_star * np.exp(1j * delta_star)
    Vt_exact, I_exact = _series_terminal_voltage(
        Ephasor, Vinf * np.exp(1j * theta_inf), Xf, Xline
    )
    S_exact = Vt_exact * np.conj(I_exact)
    Q0 = S_exact.imag

    bgfm, binf = Bus("GFM_bus"), Bus("Infinite_bus")
    grid = Grid()
    grid.add_bus(bgfm)
    grid.add_bus(binf)
    grid.add_line(Line(bgfm, binf, Xline))
    grid.add_infinite_bus(InfiniteBus(Vinf, theta_inf, F0), binf)

    pctrl = DroopController(P0=P0, kp=kp, omega0=OMEGA0)
    qctrl = VoltageDroopController(V0=E_star, Q0=Q0, kq=kq)
    gfm = GridFormingInverter(
        name="GFM",
        Hv=Hv,
        Dv=Dv,
        omega0=OMEGA0,
        power_controller=pctrl,
        voltage_controller=qctrl,
        tauE=tauE,
        Imax=5.0,
        X_filter=Xf,
    )
    grid.add_device(gfm, bgfm)
    grid.initialise()

    xeq = np.array([delta_star, OMEGA0, E_star])
    Veq = grid.algebraic_solution(xeq)
    rhs_eq = grid.derivatives(0.0, xeq)
    S_num = gfm.terminal_power(Veq[bgfm], xeq)

    assert abs(Veq[bgfm] - Vt_exact) < 1e-9
    assert abs(S_num - S_exact) < 1e-9
    assert abs(S_num.real - P0) < 1e-9
    assert np.linalg.norm(rhs_eq, ord=np.inf) < 1e-8

    x0 = xeq.copy()
    x0[0] += 0.03
    x0[2] += 0.01
    result = Simulation(grid, t_end=12.0, n_points=1201, rtol=1e-9, atol=1e-11).run(x0)
    final = result.final_state()
    assert abs(final[0] - delta_star) < 3e-3
    assert abs(final[1] - OMEGA0) < 3e-3
    assert abs(final[2] - E_star) < 3e-3

    out = {
        "delta_star_rad": delta_star,
        "E_star": E_star,
        "Q0_for_exact_equilibrium": Q0,
        "terminal_voltage": Veq[bgfm],
        "P_terminal": S_num.real,
        "Q_terminal": S_num.imag,
        "equilibrium_rhs_inf": np.linalg.norm(rhs_eq, ord=np.inf),
        "final_delta_error": final[0] - delta_star,
        "final_frequency_error_hz": (final[1] - OMEGA0) / (2 * np.pi),
        "final_E_error": final[2] - E_star,
    }
    if verbose:
        print("GFM infinite-bus validation: PASS")
        for k, v in out.items():
            print(f"  {k}: {v}")
    return out


def validate_gfl(verbose=True):
    """GFL attached to a fixed infinite bus: PI PLL + ideal PQ current source."""
    Vmag = 0.98
    theta_grid = 0.12
    Pref = 0.60
    Qref = 0.20
    Kp = 30.0
    Ki = 200.0
    Imax = 2.0

    bus = Bus("Infinite_bus")
    grid = Grid()
    grid.add_bus(bus)
    inf = InfiniteBus(Vmag, theta_grid, F0)
    grid.add_infinite_bus(inf, bus)
    gfl = GridFollowingInverter(
        name="GFL",
        Pref=Pref,
        Qref=Qref,
        omega0=OMEGA0,
        Imax=Imax,
        Kp_pll=Kp,
        Ki_pll=Ki,
    )
    grid.add_device(gfl, bus)
    grid.initialise()

    # Exact nominal-frequency PLL equilibrium: theta_hat=theta_grid, xi=0.
    xeq = np.array([theta_grid, 0.0])
    Veq = grid.algebraic_solution(xeq)
    rhs_eq = grid.derivatives(0.0, xeq)
    I_num = gfl.current_injection(Veq[bus], xeq)
    I_exact = (Pref - 1j * Qref) / np.conj(Veq[bus])
    S_num = Veq[bus] * np.conj(I_num)

    assert abs(I_exact) < Imax
    assert abs(I_num - I_exact) < 1e-12
    assert abs(S_num - (Pref + 1j * Qref)) < 1e-12
    assert np.linalg.norm(rhs_eq, ord=np.inf) < 1e-10

    x0 = np.array([theta_grid + 0.15, 0.0])
    result = Simulation(grid, t_end=2.0, n_points=801, rtol=1e-9, atol=1e-11).run(x0)
    final = result.final_state()
    final_V = grid.algebraic_solution(final)[bus]
    final_omega = gfl.pll_frequency(final_V, final)
    assert abs(final[0] - theta_grid) < 2e-4
    assert abs(final[1]) < 2e-4
    assert abs(final_omega - OMEGA0) < 2e-3

    out = {
        "theta_star_rad": theta_grid,
        "current_exact": I_exact,
        "P_terminal": S_num.real,
        "Q_terminal": S_num.imag,
        "equilibrium_rhs_inf": np.linalg.norm(rhs_eq, ord=np.inf),
        "final_theta_error": final[0] - theta_grid,
        "final_pll_frequency_error_hz": (final_omega - OMEGA0) / (2 * np.pi),
    }
    if verbose:
        print("GFL infinite-bus validation: PASS")
        for k, v in out.items():
            print(f"  {k}: {v}")
    return out


def run_all(verbose=True):
    return {
        "sg": validate_sg(verbose=verbose),
        "gfm": validate_gfm(verbose=verbose),
        "gfl": validate_gfl(verbose=verbose),
    }


if __name__ == "__main__":
    run_all(verbose=True)
