# Version 4 — rated-capacity replacement and exact disturbances

## Main changes

1. Added `Sr` and `S_base` to SG and GFM models and put physical/virtual
   inertia on the common system base using `H_system = H * Sr / S_base`.
2. Converted device-base SG/GFM reactances and damping coefficients to the
   system base as rating changes.
3. Added `Sr` to the GFL so its current capability scales with installed
   converter capacity even though its inertia remains zero.
4. Added a capacity-composition experiment in
   `experiments/capacity_composition_map.py` with independent
   `(rho_sg, rho_gfm, rho_gfl)` satisfying a simplex constraint.
5. Added exact scheduled load-step and line-trip simulation.  The integration
   is stopped exactly at the switching time, the algebraic/network mutation is
   applied, and integration is restarted from the same continuous state.
6. Repaired `LineTrip` so it cannot trip before its requested time and so it
   resets the line correctly between runs.
7. Added load-step, rating-scaling and scheduled-event regression tests.

## 2.5% composition map

The map contains 861 simplex points.

- 858 have a numerically valid pre-disturbance steady DAE equilibrium.
- 844 are also within the aggregate device apparent-power/current ratings.
- all 844 feasible equilibria have stable non-trivial linearised modes;
  no small-signal eigenvalue crossing was found for the chosen parameters.
- 14 valid points are capacity-infeasible, all in the SG-rich corner where a
  very small GFM aggregate is required to provide more apparent power than its
  assigned rating.
- the pure-GFL vertex is rejected because an island of only grid-following
  current sources has no voltage-forming reference.
- the pure-SG vertex and `(0.975,0,0.025)` fail the high-load algebraic network
  solve for this constant-PQ/network benchmark; continuation shows this is a
  voltage/power-flow feasibility issue rather than an oscillatory eigenvalue
  instability.

The least-damped feasible point on the 2.5% grid is
`(rho_sg,rho_gfm,rho_gfl)=(0.025,0.975,0)` with critical eigenvalue approximately

\[
-0.6243 \pm j 11.8914,
\]

corresponding to damping ratio about 5.24%.

## Exactly timed disturbance path

A first dynamic path keeps the displaced non-SG capacity equally divided
between GFM and GFL:

\[
\rho_{\rm GFM}=\rho_{\rm GFL}=\frac{1-\rho_{\rm SG}}{2}.
\]

A permanent `+0.10 pu P, +0.02 pu Q` load step is applied at `t=1 s`.
Reducing SG capacity increases the initial RoCoF (because total effective
inertia falls), while the final frequency error decreases in this particular
parameterisation because the installed GFM droop capacity increases.  No
current limit, loss of SG/GFM synchronism, or PLL loss of lock occurs in the
five representative load-step cases.

The SG_bus--GFL_bus diagonal line is also tripped exactly at `t=1 s`.  SG-rich
cases can lose algebraic voltage solvability after the outage even though the
pre-trip equilibrium is small-signal stable.  Along the equal GFM/GFL
replacement path:

- the *instantaneous* post-trip algebraic-solvability boundary is bracketed by
  `rho_sg = 0.54843750` and `0.54846191`;
- the 4-second transient-survival boundary is substantially lower, bracketed
  by `rho_sg = 0.50164062` and `0.50171875`.  Just above this value the
  trajectory reaches an algebraic voltage-collapse boundary about 0.31 s
  after the trip.

These boundaries are properties of this deliberately small benchmark and its
fixed line/load/controller parameters; they are not general penetration
limits for real grids.
