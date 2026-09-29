# Version 4.1 — minimal pure-SG benchmark fix

This version deliberately makes **one substantive benchmark change only** to Version 4:

- in `experiments/capacity_composition_map.py`, the direct SG-bus to GFL-bus line reactance is reduced from **0.45 pu to 0.30 pu**.

Reason: in Version 4 the 100% SG corner consisted of one fixed-excitation aggregate SG supplying two remote constant-PQ loads through a deliberately weak three-bus network. That point sat just beyond the benchmark's voltage-loadability nose. Slightly strengthening the direct transfer path makes the all-SG reference a well-conditioned equilibrium without changing the SG model, its excitation, the loads, total installed rating, dispatch rule, or the definition of the composition fractions.

At 2.5% simplex resolution the revised benchmark gives 860 valid/capacity-feasible/locally-stable operating points out of the 860 compositions containing at least one SG or GFM. The sole excluded point is 100% GFL, which has no voltage-forming reference in an islanded system.

The 100% SG point has approximately:

- minimum bus voltage = 0.83044 pu;
- SG apparent-power loading = 0.86862 of rating;
- largest non-trivial eigenvalue real part = -1.0.

This is intentionally only a benchmark repair. No AVR, general network case format, dispatch/capacity separation, island detection, richer line models, or other forward-roadmap change is implemented here.
