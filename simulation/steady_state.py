"""Steady operating-point solver for the reduced DAE grid model.

The Grid class eliminates algebraic bus voltages internally, so a steady
operating point can be found by solving

    f(x, z(x)) = 0

for the differential state ``x``.  An islanded AC system has a rotational
angle symmetry, so one angular state must be fixed as a gauge reference.
The solver therefore supports one or more fixed state values and minimizes
*all* differential residuals with an overdetermined nonlinear least-squares
solve.  At a physically consistent operating point the omitted degree of
freedom is redundant and every component of f still vanishes.
"""

from dataclasses import dataclass
import numpy as np
from scipy.optimize import least_squares


@dataclass
class SteadyStateResult:
    state: np.ndarray
    bus_voltages: dict
    differential_residual: np.ndarray
    kcl_residual: dict
    success: bool
    message: str
    nfev: int
    cost: float

    @property
    def max_differential_residual(self):
        if self.differential_residual.size == 0:
            return 0.0
        return float(np.linalg.norm(self.differential_residual, ord=np.inf))

    @property
    def max_kcl_residual(self):
        values = [abs(r) for r in self.kcl_residual.values() if r is not None]
        return float(max(values, default=0.0))


class SteadyStateSolver:
    """Solve a stationary point of a :class:`models.grid.Grid` model.

    Parameters
    ----------
    model : Grid
        Corrected DAE-reduced grid model.
    fixed_states : dict, optional
        Mapping from state index or exact ``model.state_names`` entry to a
        fixed value.  For an islanded system use one angle, e.g.
        ``{"SG_delta": 0.0}``, to remove the arbitrary global phase.
    tolerance : float
        Target nonlinear tolerance.
    max_nfev : int
        Maximum residual evaluations.
    """

    def __init__(self, model, fixed_states=None, tolerance=1e-11, max_nfev=4000):
        self.model = model
        if self.model.network is None:
            self.model.initialise()
        self.fixed_states = {} if fixed_states is None else dict(fixed_states)
        self.tolerance = float(tolerance)
        self.max_nfev = int(max_nfev)

    def _state_index(self, key):
        if isinstance(key, (int, np.integer)):
            idx = int(key)
            if idx < 0 or idx >= self.model.n_states:
                raise IndexError(f"State index {idx} is out of range.")
            return idx
        if key not in self.model.state_names:
            raise ValueError(
                f"Unknown fixed state {key!r}; available names are "
                f"{self.model.state_names}."
            )
        return self.model.state_names.index(key)

    def solve(self, x_guess=None):
        if x_guess is None:
            x_guess = self.model.initial_state()
        x_guess = np.asarray(x_guess, dtype=float).copy()
        if x_guess.shape != (self.model.n_states,):
            raise ValueError(
                f"x_guess must have shape ({self.model.n_states},), got "
                f"{x_guess.shape}."
            )

        fixed = {self._state_index(k): float(v) for k, v in self.fixed_states.items()}
        x_template = x_guess.copy()
        for idx, value in fixed.items():
            x_template[idx] = value

        free = np.array([i for i in range(self.model.n_states) if i not in fixed], dtype=int)

        def unpack(y):
            x = x_template.copy()
            x[free] = y
            return x

        def residual(y):
            x = unpack(y)
            return np.asarray(self.model.derivatives(0.0, x), dtype=float)

        # A stale voltage warm-start from a remote trajectory point can be a
        # poor initial guess for a nonlinear equilibrium solve.
        self.model._voltage_guess = None
        sol = least_squares(
            residual,
            x_template[free],
            xtol=self.tolerance,
            ftol=self.tolerance,
            gtol=self.tolerance,
            max_nfev=self.max_nfev,
            x_scale="jac",
        )
        x = unpack(sol.x)
        self.model._voltage_guess = None
        V = self.model.algebraic_solution(x)
        f = np.asarray(self.model.derivatives(0.0, x), dtype=float)
        kcl = self.model.power_balance_residual(x)

        return SteadyStateResult(
            state=x,
            bus_voltages=V,
            differential_residual=f,
            kcl_residual=kcl,
            success=bool(sol.success),
            message=str(sol.message),
            nfev=int(sol.nfev),
            cost=float(sol.cost),
        )
