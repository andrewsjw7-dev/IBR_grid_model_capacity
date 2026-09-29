# Mixed SG-GFM-GFL steady-DAE baseline (Version 3)

## Purpose

Version 3 reconnects the three validated device models only after constructing
an islanded steady operating point satisfying the coupled differential and
algebraic equations.  No arbitrary zero-angle initial condition is used as a
proxy for a power-flow solution.

The benchmark contains three buses in a lossless mesh:

- SG bus: synchronous generator;
- GFM bus: grid-forming inverter plus a 0.35 + j0.10 pu PQ load;
- GFL bus: grid-following inverter plus a 1.15 + j0.25 pu PQ load.

Line reactances are 0.25, 0.30 and 0.45 pu.  The default active dispatch is

\[
P_{\rm SG}=0.60,\qquad P_{\rm GFM}=0.50,\qquad P_{\rm GFL}=0.40,
\]

so that

\[
P_{\rm gen}=1.50=P_{\rm load}.
\]

## Steady DAE solve

The algebraic bus voltages are eliminated by the KCL solve already introduced
in Version 2.  The steady solver then seeks

\[
f(x,z(x))=0.
\]

An islanded AC network is invariant under a common phase rotation.  We remove
only this gauge freedom by imposing

\[
\delta_{\rm SG}=0.
\]

All components of the differential residual are nevertheless retained in the
nonlinear least-squares objective.  Hence a successful solution must satisfy
all dynamic equilibrium equations, including the SG active-power equation,
rather than silently dropping one equation.

## Required validation identities

At the returned state we check

\[
\|f\|_\infty < 10^{-9},\qquad
\|g\|_\infty < 10^{-9},
\]

and, because every electrical element is lossless in active power,

\[
\sum_d P_d-\sum_L P_L=0.
\]

For reactive power, the series reactances absorb reactive power.  Therefore the
correct check is

\[
\sum_d Q_d-\sum_L Q_L
-
\sum_{\ell} X_\ell |I_\ell|^2
=0,
\]

not simply \(\sum Q_{\rm gen}=\sum Q_{\rm load}\).

The GFL is additionally required to satisfy its commanded terminal power and
PLL lock, and both inverter current limits must remain inactive in this
baseline.

## Perturbation validation

After solving the equilibrium, three simultaneous small perturbations are
applied: SG speed +0.03 Hz, GFM angle +0.025 rad and GFL PLL phase -0.020 rad.
The system must return to nominal frequency and to the same *relative* angles
and terminal powers.  Absolute angle is not tested because an islanded system
may acquire an arbitrary common phase shift.

## First IBR penetration sweep

`experiments/ibr_penetration_sweep.py` begins a deliberately limited first
study by varying the active-power dispatch share supplied by IBRs while holding
the IBR split at GFM:GFL = 5:4.  The 60% point therefore reproduces the
validated 0.60/0.50/0.40 SG/GFM/GFL dispatch.

This is explicitly a **dispatch-penetration** study.  The SG and GFM stay
online and their inertia parameters do not scale with dispatched MW.  It must
not yet be interpreted as physical replacement of synchronous installed
capacity.  A true capacity-displacement study requires device MVA ratings and
conversion of each inertia constant to the common system base before changing
penetration.
