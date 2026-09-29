> **Version 2 historical note:** this file records the state before the mixed-system Version 3 extension. See `VERSION_3_NOTES.md` for the current status.

# Baseline revision notes

## Scope of this revision

This revision deliberately stops after the three independently validated
single-device cases.  It does **not** yet claim a validated mixed SG-GFM-GFL
system or IBR-penetration study.

## Main changes

- Replaced the old `first device on a bus -> bus voltage` rule by nonlinear
  algebraic KCL equations solved at every differential RHS evaluation.
- Corrected the network complex-power sign convention to `S = V conj(YV)`.
- Added ideal infinite-bus boundary conditions at selected buses.
- Changed SG electrical coupling to an internal EMF behind `Xd_prime`.
- Added the preferred physical inertia parameter `H`; legacy `M` remains for
  compatibility.
- Changed GFM coupling to an internal controlled voltage behind `X_filter`.
- Added the preferred virtual inertia parameter `Hv`; legacy `Mv` remains for
  compatibility.
- Corrected the standalone GFM power-angle sign.
- Activated GFM current limiting through the existing `CurrentLimiter` class.
- Replaced the self-referential GFL bus-angle model by a measured-bus SRF-PLL.
- Made the GFL an ideal `P,Q` current source with current limiting.
- Made constant-PQ loads enter the network as voltage-dependent current draws.
- Device electrical powers are now computed per device, so multiple devices on
  one bus no longer each receive the whole bus power.
- `SynchronousGenerator.derivatives()` now calls `mechanical_power(t)`, so the
  existing subclassing pattern for mechanical-power disturbances works.
- Added exact-equilibrium validation problems and tests.

## Validation status

`python -m validation.baseline_validations` and `pytest` both pass.

The old `tests/` directory is retained as development history; many files in
it target superseded constructor/API conventions.  `pytest.ini` therefore
points default test discovery at the new `validation/` tests only.

## Deliberately deferred

Before IBR-penetration experiments, the next stage should:

1. construct and initialize a mixed SG-GFM-GFL operating point by solving the
   combined steady DAE;
2. validate total active/reactive power balance and per-device sharing;
3. repair switching/disturbance integration so topology events occur exactly
   at their specified times (prefer piecewise integration at known event times);
4. only then perform line-trip/load-step penetration sweeps.
