"""Validated mixed SG-GFM-GFL islanded operating point.

This is the first coupled benchmark after the three single-device tests.
It deliberately solves the steady DAE before integrating a trajectory.

Run from the repository root with

    python -m validation.mixed_system_validation
"""

import numpy as np

from controls.droop import DroopController
from controls.voltage_droop import VoltageDroopController
from models.bus import Bus
from models.grid import Grid
from models.grid_following_inverter import GridFollowingInverter
from models.grid_forming_inverter import GridFormingInverter
from models.line import Line
from models.load import Load
from models.synchronous_generator import SynchronousGenerator
from simulation.solver import Simulation
from simulation.steady_state import SteadyStateSolver


F0 = 50.0
OMEGA0 = 2 * np.pi * F0


def build_mixed_system(Psg=0.60, Pgfm=0.50, Pgfl=0.40, Qgfl=0.10):
    """Construct the three-bus lossless mixed benchmark.

    Total active load is 1.50 pu.  The default dispatch therefore satisfies
    Psg + Pgfm + Pgfl = Pload exactly, allowing a nominal-frequency islanded
    equilibrium.
    """
    bsg = Bus("SG_bus")
    bgfm = Bus("GFM_bus")
    bgfl = Bus("GFL_bus")

    grid = Grid()
    for bus in (bsg, bgfm, bgfl):
        grid.add_bus(bus)

    # Meshed network: this avoids making the benchmark dependent on a single
    # radial transfer path and exercises all bus KCL equations simultaneously.
    grid.add_line(Line(bsg, bgfm, 0.25))
    grid.add_line(Line(bgfm, bgfl, 0.30))
    grid.add_line(Line(bsg, bgfl, 0.45))

    # Distributed load rather than a single aggregate load.
    grid.add_load(Load("Load_GFM_bus", P=0.35, Q=0.10), bgfm)
    grid.add_load(Load("Load_GFL_bus", P=1.15, Q=0.25), bgfl)

    sg = SynchronousGenerator(
        name="SG",
        H=5.0,
        D=10.0,
        Pm=Psg,
        omega0=OMEGA0,
        E_internal=1.05,
        Xd_prime=0.20,
    )

    pctrl = DroopController(P0=Pgfm, kp=0.10, omega0=OMEGA0)
    qctrl = VoltageDroopController(V0=1.03, Q0=0.0, kq=0.06)
    gfm = GridFormingInverter(
        name="GFM",
        Hv=2.5,
        Dv=8.0,
        omega0=OMEGA0,
        power_controller=pctrl,
        voltage_controller=qctrl,
        tauE=0.08,
        Imax=3.0,
        X_filter=0.15,
    )

    gfl = GridFollowingInverter(
        name="GFL",
        Pref=Pgfl,
        Qref=Qgfl,
        omega0=OMEGA0,
        Imax=2.0,
        Kp_pll=30.0,
        Ki_pll=200.0,
    )

    for device, bus in ((sg, bsg), (gfm, bgfm), (gfl, bgfl)):
        grid.add_device(device, bus)
    grid.initialise()

    return grid, {"sg": sg, "gfm": gfm, "gfl": gfl}, {
        "sg": bsg, "gfm": bgfm, "gfl": bgfl
    }


def solve_mixed_equilibrium(Psg=0.60, Pgfm=0.50, Pgfl=0.40, Qgfl=0.10):
    grid, devices, buses = build_mixed_system(Psg, Pgfm, Pgfl, Qgfl)
    x_guess = grid.initial_state()
    x_guess[grid.device_state_indices[devices["gfm"]].start + 2] = 1.03

    # Islanded AC networks have arbitrary global phase.  Fix the SG internal
    # angle to zero as the gauge, while still requiring *all* entries of f to
    # vanish in the overdetermined least-squares solve.
    solver = SteadyStateSolver(grid, fixed_states={"SG_delta": 0.0})
    steady = solver.solve(x_guess)
    return grid, devices, buses, steady


def validate_mixed_equilibrium(verbose=True):
    grid, devices, buses, steady = solve_mixed_equilibrium()
    xeq = steady.state
    diag = grid.operating_point_diagnostics(xeq)
    V = diag["bus_voltages"]
    S = diag["device_powers"]

    sg, gfm, gfl = devices["sg"], devices["gfm"], devices["gfl"]

    assert steady.success
    assert steady.max_differential_residual < 1e-9
    assert steady.max_kcl_residual < 1e-9
    assert abs(diag["active_power_balance"]) < 1e-10
    assert abs(diag["reactive_balance_residual"]) < 1e-10

    assert abs(S[sg].real - 0.60) < 1e-9
    assert abs(S[gfm].real - 0.50) < 1e-9
    assert abs(S[gfl].real - 0.40) < 1e-12
    assert abs(S[gfl].imag - 0.10) < 1e-12

    sg_state = grid.get_device_state(xeq, sg)
    gfm_state = grid.get_device_state(xeq, gfm)
    gfl_state = grid.get_device_state(xeq, gfl)
    assert abs(sg_state[1] - OMEGA0) < 1e-10
    assert abs(gfm_state[1] - OMEGA0) < 1e-10
    assert abs(gfl.phase_detector(V[buses["gfl"]], gfl_state)) < 1e-10
    assert abs(gfl_state[1]) < 1e-10

    # Current limiters must be inactive in the baseline equilibrium, otherwise
    # the requested P/Q sharing would not be the unconstrained solution.
    currents = {
        name: abs(device.current_injection(V[buses[name]], grid.get_device_state(xeq, device)))
        for name, device in devices.items()
    }
    assert currents["gfm"] < gfm.Imax - 1e-6
    assert currents["gfl"] < gfl.Imax - 1e-6

    out = {
        "state": xeq,
        "bus_voltages": V,
        "device_powers": S,
        "currents": currents,
        "P_generation": diag["P_generation"],
        "P_load": diag["P_load"],
        "Q_generation": diag["Q_generation"],
        "Q_load": diag["Q_load"],
        "Q_line_absorption": diag["reactive_network_absorption"],
        "active_power_balance": diag["active_power_balance"],
        "reactive_balance_residual": diag["reactive_balance_residual"],
        "rhs_inf": steady.max_differential_residual,
        "kcl_inf": steady.max_kcl_residual,
        "nfev": steady.nfev,
    }

    if verbose:
        print("Mixed SG-GFM-GFL steady-DAE validation: PASS")
        print(f"  nonlinear evaluations: {steady.nfev}")
        print(f"  max |f|: {steady.max_differential_residual:.3e}")
        print(f"  max |KCL|: {steady.max_kcl_residual:.3e}")
        print(f"  P generation/load: {diag['P_generation']:.12f} / {diag['P_load']:.12f}")
        print(f"  Q generation/load/lines: {diag['Q_generation']:.12f} / "
              f"{diag['Q_load']:.12f} / {diag['reactive_network_absorption']:.12f}")
        for name, bus in buses.items():
            print(f"  V_{name}: {abs(V[bus]):.9f} pu @ {np.angle(V[bus]):.9f} rad")
        for name, device in devices.items():
            sd = S[device]
            print(f"  S_{name}: {sd.real:.12f} + j{sd.imag:.12f} pu")
    return out


def validate_mixed_perturbation(verbose=True):
    """Perturb several dynamic states and require recovery modulo angle gauge."""
    grid, devices, buses, steady = solve_mixed_equilibrium()
    xeq = steady.state
    x0 = xeq.copy()

    sg_slice = grid.device_state_indices[devices["sg"]]
    gfm_slice = grid.device_state_indices[devices["gfm"]]
    gfl_slice = grid.device_state_indices[devices["gfl"]]

    x0[sg_slice.start + 1] += 2 * np.pi * 0.03   # +0.03 Hz SG speed
    x0[gfm_slice.start] += 0.025                  # GFM angle displacement
    x0[gfl_slice.start] -= 0.020                  # PLL phase displacement

    result = Simulation(
        grid, t_end=20.0, n_points=2001, rtol=1e-9, atol=1e-11
    ).run(x0)
    xf = result.final_state()
    Vf = grid.algebraic_solution(xf)
    rhsf = grid.derivatives(20.0, xf)

    # Absolute angles may acquire a common offset in an islanded system.  The
    # physically meaningful tests are relative angles, frequencies, PLL lock,
    # voltages and terminal powers.
    rel_eq = xeq[gfm_slice.start] - xeq[sg_slice.start]
    rel_f = xf[gfm_slice.start] - xf[sg_slice.start]
    pll_error = xf[gfl_slice.start] - np.angle(Vf[buses["gfl"]])

    Sf = grid.device_powers(xf, Vf)
    pll_freq = devices["gfl"].pll_frequency(
        Vf[buses["gfl"]], grid.get_device_state(xf, devices["gfl"])
    )

    assert abs(xf[sg_slice.start + 1] - OMEGA0) < 2e-6
    assert abs(xf[gfm_slice.start + 1] - OMEGA0) < 2e-6
    assert abs(pll_freq - OMEGA0) < 2e-6
    assert abs(rel_f - rel_eq) < 2e-6
    assert abs(pll_error) < 2e-6
    assert np.linalg.norm(rhsf, ord=np.inf) < 2e-8
    assert abs(Sf[devices["sg"]].real - 0.60) < 2e-7
    assert abs(Sf[devices["gfm"]].real - 0.50) < 2e-7
    assert abs(Sf[devices["gfl"]].real - 0.40) < 2e-12

    out = {
        "final_rhs_inf": float(np.linalg.norm(rhsf, ord=np.inf)),
        "final_sg_frequency_error_hz": float(
            (xf[sg_slice.start + 1] - OMEGA0) / (2 * np.pi)
        ),
        "final_gfm_frequency_error_hz": float(
            (xf[gfm_slice.start + 1] - OMEGA0) / (2 * np.pi)
        ),
        "final_pll_frequency_error_hz": float((pll_freq - OMEGA0) / (2 * np.pi)),
        "final_relative_angle_error_rad": float(rel_f - rel_eq),
        "final_pll_angle_error_rad": float(pll_error),
        "common_angle_shift_rad": float(xf[sg_slice.start] - xeq[sg_slice.start]),
    }
    if verbose:
        print("Mixed-system perturbation recovery: PASS")
        for key, value in out.items():
            print(f"  {key}: {value}")
    return out


def run_all(verbose=True):
    return {
        "equilibrium": validate_mixed_equilibrium(verbose=verbose),
        "perturbation": validate_mixed_perturbation(verbose=verbose),
    }


if __name__ == "__main__":
    run_all(verbose=True)
