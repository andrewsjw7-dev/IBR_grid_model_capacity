"""First IBR-penetration sweep from the validated mixed operating point.

IMPORTANT
---------
This first sweep varies *active-power dispatch share* while leaving the SG and
GFM dynamic parameters/on-line capacity unchanged.  It is therefore a
"dispatch penetration" study, not yet a physically complete generator-
replacement study.  A capacity-displacement study must additionally scale
machine/converter ratings and system-base inertia contributions.

The GFM:GFL IBR active-power split is held at 5:4, so penetration=0.60 exactly
recovers the validated 0.60/0.50/0.40 SG/GFM/GFL baseline.
"""

import csv
from pathlib import Path
import numpy as np

from validation.mixed_system_validation import solve_mixed_equilibrium


TOTAL_ACTIVE_LOAD = 1.50
GFM_IBR_FRACTION = 5.0 / 9.0
GFL_IBR_FRACTION = 4.0 / 9.0


def _linearised_jacobian(grid, xeq):
    """Central finite-difference Jacobian of the algebraically reduced ODE."""
    xeq = np.asarray(xeq, dtype=float)
    n = len(xeq)
    J = np.zeros((n, n))
    for j in range(n):
        name = grid.state_names[j]
        if "omega" in name:
            h = 1e-5
        elif name.endswith("_E"):
            h = 1e-6
        elif name.endswith("_xi"):
            h = 1e-7
        else:
            h = 1e-6
        xp = xeq.copy()
        xm = xeq.copy()
        xp[j] += h
        xm[j] -= h
        grid._voltage_guess = None
        fp = grid.derivatives(0.0, xp)
        grid._voltage_guess = None
        fm = grid.derivatives(0.0, xm)
        J[:, j] = (fp - fm) / (2 * h)
    return J


def run_sweep(penetrations=None, csv_path=None, verbose=True):
    if penetrations is None:
        penetrations = np.linspace(0.0, 1.0, 11)

    rows = []
    previous_state = None

    for rho in penetrations:
        rho = float(rho)
        Pibr = rho * TOTAL_ACTIVE_LOAD
        Pgfm = GFM_IBR_FRACTION * Pibr
        Pgfl = GFL_IBR_FRACTION * Pibr
        Psg = TOTAL_ACTIVE_LOAD - Pibr

        grid, devices, buses, steady = solve_mixed_equilibrium(
            Psg=Psg, Pgfm=Pgfm, Pgfl=Pgfl, Qgfl=0.10
        )
        xeq = steady.state
        diag = grid.operating_point_diagnostics(xeq)
        V = diag["bus_voltages"]

        J = _linearised_jacobian(grid, xeq)
        eig = np.linalg.eigvals(J)
        # Rotational symmetry creates one zero eigenvalue.  Remove only the
        # eigenvalue closest to zero before judging local asymptotic modes.
        zero_index = np.argmin(np.abs(eig))
        rotational_eigenvalue = eig[zero_index]
        nontrivial = np.delete(eig, zero_index)
        critical = nontrivial[np.argmax(nontrivial.real)]
        critical_abs = abs(critical)
        critical_damping_ratio = (
            -critical.real / critical_abs if critical_abs > 0.0 else np.nan
        )
        critical_mode_frequency_hz = abs(critical.imag) / (2 * np.pi)

        currents = {}
        for name, device in devices.items():
            bus = buses[name]
            state = grid.get_device_state(xeq, device)
            currents[name] = abs(device.current_injection(V[bus], state))

        row = {
            "ibr_dispatch_fraction": rho,
            "P_sg": Psg,
            "P_gfm": Pgfm,
            "P_gfl": Pgfl,
            "max_differential_residual": steady.max_differential_residual,
            "max_kcl_residual": steady.max_kcl_residual,
            "active_power_balance": diag["active_power_balance"],
            "min_bus_voltage_pu": min(abs(V[b]) for b in buses.values()),
            "max_sg_current_pu": currents["sg"],
            "max_gfm_current_pu": currents["gfm"],
            "max_gfl_current_pu": currents["gfl"],
            "rotational_eigenvalue_abs": float(abs(rotational_eigenvalue)),
            "critical_eigenvalue_real": float(critical.real),
            "critical_eigenvalue_imag": float(critical.imag),
            "critical_mode_frequency_hz": float(critical_mode_frequency_hz),
            "critical_damping_ratio": float(critical_damping_ratio),
            "locally_stable_nontrivial_modes": bool(np.max(nontrivial.real) < 0.0),
        }
        rows.append(row)
        previous_state = xeq

        if verbose:
            print(
                f"rho={rho:4.2f}  P=[{Psg:.3f}, {Pgfm:.3f}, {Pgfl:.3f}]  "
                f"min|V|={row['min_bus_voltage_pu']:.4f}  "
                f"lambda_crit={critical.real:+.4f}{critical.imag:+.4f}j"
            )

    if csv_path is not None:
        path = Path(csv_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    return rows


if __name__ == "__main__":
    run_sweep(csv_path="ibr_dispatch_penetration_sweep.csv", verbose=True)
