# Version 3 revision notes

Version 3 follows the Version 2 single-device DAE validations and adds the
first validated mixed SG-GFM-GFL operating point.

## Added

- `simulation/steady_state.py`: nonlinear steady-state solver with explicit
  angle-gauge constraints for islanded systems.
- `Grid.device_powers()` and operating-point power/KCL diagnostics.
- Exact active-power balance and correct reactive-series-absorption checks.
- `validation/mixed_system_validation.py`: coupled three-bus equilibrium plus
  transient recovery from simultaneous SG/GFM/GFL perturbations.
- `validation/test_mixed_system.py`: automated regression tests.
- `experiments/ibr_penetration_sweep.py`: first dispatch-based IBR share sweep
  with numerical small-signal eigenvalue calculation.
- `MIXED_SYSTEM_BASELINE.md`: mathematical definition and interpretation.

## Scientific boundary retained

The first penetration sweep changes dispatch only.  It does not yet represent
retirement/replacement of synchronous capacity, because SG/GFM ratings and
system-base inertia contributions are not yet explicit model parameters.

## Still deferred before severe-disturbance penetration studies

1. Add explicit device MVA ratings and common-system-base inertia scaling.
2. Repair known-time switching as piecewise integration rather than mutable
   topology changes inside an adaptive RK RHS.
3. Add a validated load-step disturbance and then a line-trip/fault sequence.
4. Define penetration scenarios that separately vary GFM share, GFL share and
   synchronous online capacity rather than conflating all IBRs.
