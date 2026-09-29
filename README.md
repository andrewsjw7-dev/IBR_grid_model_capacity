# IBR Grid Model — Version 4.1

Reduced-order dynamic modelling of mixed synchronous-generator (SG), grid-forming inverter (GFM), and grid-following inverter (GFL) power systems.

This repository contains **Version 4.1** of the model developed from the ESGI 195 grid-stability work. The code has been reworked into a consistent differential-algebraic network model and extended to study genuine **installed-capacity replacement** between SG, GFM, and GFL technologies.

The central Version 4.1 experiment is a three-bus composition study in which the installed generation mix

$$\rho_{\mathrm{SG}}+\rho_{\mathrm{GFM}}+\rho_{\mathrm{GFL}}=1$$


is varied across the complete SG–GFM–GFL simplex while demand is held fixed.

---

## What Version 4.1 changes

Version 4.1 makes one deliberate benchmark change relative to Version 4:

- the direct line reactance between the SG and GFL buses is reduced from **0.45 pu to 0.30 pu** in `experiments/capacity_composition_map.py`.

The Version 4 all-SG point consisted of one fixed-excitation aggregate SG supplying two remote constant-\(PQ\) loads through a weak three-bus network. That point lay just beyond the benchmark's voltage-loadability nose. Strengthening the direct transfer path makes the **100% SG case a well-conditioned reference equilibrium** without changing:

- the SG model or excitation;
- the loads;
- total installed generation rating;
- the capacity-fraction definitions;
- the dispatch rule;
- the GFM or GFL models.

This is a benchmark repair, not a claim that \(X=0.30\) pu represents a particular real transmission network.

At 2.5% composition resolution, Version 4.1 gives:

- **861** compositions tested;
- **860** valid and capacity-feasible equilibria;
- **860/860** feasible cases locally small-signal stable;
- one excluded point: **100% GFL**, because an island containing only grid-following current sources has no voltage-forming reference.

At the 100% SG point:

- minimum bus voltage: approximately **0.83044 pu**;
- SG apparent-power loading: approximately **0.86862** of rating;
- largest non-trivial eigenvalue real part: approximately **-1.0**.

The least-damped feasible point on the 2.5% grid is near

$$(\rho_{\mathrm{SG}},\rho_{\mathrm{GFM}},\rho_{\mathrm{GFL}})
=(0.025,0.975,0),$$

with critical eigenvalue approximately

$$\lambda=-0.6248 \pm 11.9349\,i,$$

corresponding to a mode at approximately **1.90 Hz** with damping ratio approximately **5.23%**.

---

## Model structure

The electrical network is treated as a reduced differential-algebraic system,

$$\dot{x}=f(x,z), \qquad 0=g(x,z),$$

where \(x\) contains dynamic device states and \(z\) contains the algebraic bus voltages.

At each bus, Kirchhoff's current law is enforced using the network admittance matrix. Constant-\(PQ\) loads are represented by

$$I_L=\frac{P_L-jQ_L}{V^*}.$$

The benchmark currently uses lossless lines.

### Synchronous generator

The SG is represented as an internal voltage source behind transient reactance. Its physical inertia is placed on the common system base,

$$H_{\mathrm{sys}}=H\frac{S_r}{S_B},
\qquad
M_{\mathrm{sys}}=\frac{2HS_r}{\omega_0S_B}.$$

Its transient reactance and damping are also converted from device base to system base as the aggregate rating changes.

This is important: reducing SG capacity now genuinely reduces synchronous inertia instead of merely reducing the mechanical-power setpoint of an unchanged machine.

### Grid-forming inverter

The GFM is represented as a controlled voltage source behind filter/virtual reactance, with:

- virtual inertia;
- active-power/frequency droop;
- reactive-power/voltage droop;
- converter current limiting.

Its virtual inertia, damping, reactance, droop scaling, and current capability are converted consistently as installed GFM rating changes.

### Grid-following inverter

The GFL is represented as a controlled current source with a reduced PLL model. It does not establish the island voltage or phase.

The GFL has no swing inertia, but it has an explicit rating \(S_r\), so its current capability scales with installed capacity.

---

## Capacity fractions

The installed-capacity fractions are

$$\rho_{\mathrm{SG}}
=
\frac{\sum S_{r,\mathrm{SG}}}
     {\sum S_r},
\qquad
\rho_{\mathrm{GFM}}
=
\frac{\sum S_{r,\mathrm{GFM}}}
     {\sum S_r},
\qquad
\rho_{\mathrm{GFL}}
=
\frac{\sum S_{r,\mathrm{GFL}}}
     {\sum S_r}.$$

These are **fractions of installed apparent-power rating**, not fractions of the number of generating units.

In the current benchmark only, active-power dispatch is chosen proportional to installed capacity:

$$P_i=\rho_i P_L.$$

This is an experimental assumption, not part of the definition of \(\rho_i\). A future version should separate installed-capacity share from instantaneous dispatch share.

---

## Version 4.1 benchmark

The capacity-composition experiment uses a three-bus meshed island:

- SG at the SG bus;
- GFM at the GFM bus;
- GFL at the GFL bus.

Line reactances are:

$$X_{\mathrm{SG,GFM}}=0.25,
\qquad
X_{\mathrm{GFM,GFL}}=0.30,
\qquad
X_{\mathrm{SG,GFL}}=0.30
\quad \mathrm{pu}.$$

Loads are:

$$S_{\mathrm{Load,GFM}}=0.35+j0.10,$$

$$S_{\mathrm{Load,GFL}}=1.15+j0.25
\quad \mathrm{pu}.$$

Hence

$$P_L=1.50,\qquad Q_L=0.35 \quad \mathrm{pu}.$$

The total installed generation rating is

$$S_{\mathrm{total}}=2.0 \quad \mathrm{pu},$$

so proportional dispatch corresponds to 75% active loading before reactive-power requirements are included.

---

## Composition triangle

The primary Version 4.1 output is:

```text
ibr_capacity_composition_map_0025_v4_1.csv
```

The simplex is sampled at

$$\Delta \rho=0.025,$$

giving 861 compositions.

For each composition the code:

1. builds the appropriately rated SG/GFM/GFL fleet;
2. removes technologies whose rating is exactly zero;
3. solves a steady DAE operating point;
4. checks differential and KCL residuals;
5. checks active- and reactive-power balance;
6. checks apparent-power ratings and converter current limits;
7. numerically linearises the reduced differential dynamics;
8. removes the neutral rotational-symmetry mode;
9. records the critical non-trivial eigenvalue and damping information.

Run the Version 4.1 composition map from the repository root with:

```bash
python -m experiments.capacity_composition_map
```

This writes:

```text
ibr_capacity_composition_map_0025.csv
```

using the **current code**, which in Version 4.1 contains the revised 0.30 pu SG–GFL line.

For archival clarity, the repository also contains:

```text
ibr_capacity_composition_map_0025_v4_1.csv
```

which is the saved Version 4.1 result set used for the report.

---

## Reproducing a triangle plot

The repository stores the composition data as CSV. A ternary-style triangle can be plotted in ordinary Cartesian coordinates using

$$x=\rho_{\mathrm{GFM}}+\frac{1}{2}\rho_{\mathrm{GFL}},
\qquad
y=\frac{\sqrt{3}}{2}\rho_{\mathrm{GFL}}.$$

For example:

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("ibr_capacity_composition_map_0025_v4_1.csv")

x = df["rho_gfm"] + 0.5 * df["rho_gfl"]
y = (np.sqrt(3) / 2) * df["rho_gfl"]

feasible = df["capacity_feasible"].fillna(False).astype(bool)
no_ref = df["status"].eq("no_voltage_forming_reference")

fig, ax = plt.subplots(figsize=(8, 7))

ax.plot(
    [0, 1, 0.5, 0],
    [0, 0, np.sqrt(3) / 2, 0],
)

sc = ax.scatter(
    x[feasible],
    y[feasible],
    c=df.loc[feasible, "max_nontrivial_real_part"],
    s=25,
)

ax.scatter(
    x[no_ref],
    y[no_ref],
    marker="s",
    s=60,
    label="No voltage-forming reference",
)

ax.text(-0.03, -0.035, "100% SG", ha="right", va="top")
ax.text(1.03, -0.035, "100% GFM", ha="left", va="top")
ax.text(
    0.5,
    np.sqrt(3) / 2 + 0.035,
    "100% GFL",
    ha="center",
    va="bottom",
)

ax.set_aspect("equal")
ax.set_xticks([])
ax.set_yticks([])
ax.set_title("SG–GFM–GFL capacity composition")

cbar = fig.colorbar(sc, ax=ax)
cbar.set_label("Largest non-trivial eigenvalue real part")

ax.legend()
fig.tight_layout()
plt.show()
```

The vertices correspond to:

- lower left: 100% SG;
- lower right: 100% GFM;
- top: 100% GFL.

Points on an edge contain only the two technologies at the ends of that edge. Interior points contain all three.

The colour represents

\[
\alpha=\max_{\lambda_j\neq 0}\Re(\lambda_j),
\]

after removing the neutral common-angle mode. A negative value indicates local small-signal stability; values closer to zero indicate a smaller local damping margin.

---

## Installation

The code is pure Python and currently depends on:

- NumPy;
- SciPy;
- Matplotlib;
- pytest, for the validation suite.

A minimal environment can be created with:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install numpy scipy matplotlib pytest
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

Run commands from the repository root so that the package-level imports resolve correctly.

---

## Validation and tests

Run the regression suite with:

```bash
python -m pytest
```

For Version 4.1 the validation suite contains **10 passing tests**, covering:

- SG common-base scaling;
- GFM common-base scaling;
- GFL rating/current-capability scaling;
- SG infinite-bus validation;
- GFM infinite-bus validation;
- GFL infinite-bus validation;
- mixed-system steady-state checks;
- perturbation recovery;
- exact load-step timing;
- line-trip timing and reset behaviour.

Individual validation scripts can also be run directly:

```bash
python -m validation.baseline_validations
python -m validation.mixed_system_validation
```

---

## Scheduled disturbances

Version 4 introduced an exact event scheduler for topology and load changes.

A disturbance simulation is integrated up to the specified event time, stopped exactly at that time, the network/load mutation is applied, and integration then restarts from the same continuous dynamic state.

Implemented event types include:

- `LoadStep`;
- `LineTrip`.

The disturbance driver is:

```bash
python -m experiments.dynamic_capacity_disturbances
```

and the line-trip boundary study is:

```bash
python -m experiments.line_trip_security_boundary
```

### Important Version 4.1 provenance note

The file

```text
ibr_capacity_dynamic_disturbances.csv
```

bundled in this repository contains results generated for the **earlier Version 4 benchmark**. Its stored static operating-point metrics do not match the revised Version 4.1 composition map.

The disturbance scripts import the current `capacity_composition_map.py`, so **rerunning them now uses the Version 4.1 network**, but the bundled Version 4 disturbance CSV should not be cited as a Version 4.1 result without rerunning the experiment.

The same caution should be applied to older stored Version 3/4 outputs retained for provenance.

---

## Repository layout

```text
IBR_grid_model/
├── controls/
│   ├── controller.py
│   ├── current_limiter.py
│   ├── droop.py
│   └── voltage_droop.py
├── converters/
│   └── converter.py
├── disturbances/
│   ├── disturbance.py
│   ├── line_trip.py
│   └── load_step.py
├── experiments/
│   ├── capacity_composition_map.py
│   ├── dynamic_capacity_disturbances.py
│   ├── experiment_01_sg_infinite_bus.py
│   ├── ibr_penetration_sweep.py
│   └── line_trip_security_boundary.py
├── models/
│   ├── bus.py
│   ├── grid.py
│   ├── grid_following_inverter.py
│   ├── grid_forming_inverter.py
│   ├── infinite_bus.py
│   ├── line.py
│   ├── load.py
│   ├── network.py
│   └── synchronous_generator.py
├── simulation/
│   ├── results.py
│   ├── scheduled.py
│   ├── solver.py
│   └── steady_state.py
├── validation/
│   ├── baseline_validations.py
│   ├── mixed_system_validation.py
│   ├── test_baseline.py
│   ├── test_capacity_scaling.py
│   ├── test_mixed_system.py
│   └── test_scheduled_events.py
├── CAPACITY_COMPOSITION_MODEL.md
├── MATHEMATICAL_BASELINE.md
├── MIXED_SYSTEM_BASELINE.md
├── VERSION_3_NOTES.md
├── VERSION_4_NOTES.md
├── VERSION_4_1_NOTES.md
└── pytest.ini
```

The repository also retains older experiments, tests, notes, and CSV outputs as a development record. For the Version 4.1 composition study, the key files are:

```text
experiments/capacity_composition_map.py
ibr_capacity_composition_map_0025_v4_1.csv
VERSION_4_1_NOTES.md
CAPACITY_COMPOSITION_MODEL.md
validation/test_capacity_scaling.py
```

---

## Current limitations

Version 4.1 is a **reduced research benchmark**, not a production power-system simulator.

Important limitations include:

- the composition experiment uses one aggregate SG, one aggregate GFM, and one aggregate GFL;
- the three technologies occupy fixed buses;
- capacity share and dispatch share are coupled in the current benchmark;
- the SG has no turbine governor or AVR/excitation dynamics;
- the GFM is a reduced virtual-swing/droop model;
- the GFL is an idealised current-source/PLL model;
- lines are lossless reactances only;
- loads are constant-\(PQ\);
- transformers, tap changers, shunts, and detailed protection are not included;
- automatic island detection and per-island reference handling are not yet implemented;
- the small-signal Jacobian is computed numerically;
- the benchmark has not yet been calibrated to a specific real transmission network.

The fact that all 860 voltage-forming compositions are locally stable in the Version 4.1 triangle should therefore **not** be interpreted as a universal statement about SG/GFM/GFL mixtures.

---

## Intended next steps

The most important architectural changes are:

1. separate **network**, **generation fleet**, **operating point**, and **experiment** definitions;
2. make \(\rho\) exclusively an installed-capacity statistic and introduce independent dispatch variables;
3. support arbitrary numbers and placements of SG/GFM/GFL devices;
4. add automatic electrical-island detection and one phase gauge per island;
5. add SG governor and AVR/excitation models;
6. extend the network model to \(R+jX\) lines, shunts, and transformers;
7. add ZIP loads and richer converter current limiting;
8. compute a proper reduced-DAE Jacobian and modal participation factors;
9. validate against established power-system test cases.

Scientifically interesting transition experiments then include:

- SG \(\rightarrow\) GFM versus SG \(\rightarrow\) GFL replacement;
- installed capacity versus actual dispatch;
- minimum GFM fraction at fixed total IBR penetration;
- identical capacity mixes at different geographical locations;
- synchronous-generator retirement versus synchronous-condenser retention;
- inertia versus GFM fast frequency response;
- generator-loss, load-step, line-outage, and fault studies;
- current-limit activation;
- weak-grid/system-strength sweeps;
- \(N-1\) security across the composition triangle.

---

## Development notes

The repository contains a sequence of notes describing the progression from the original prototype to the current model:

- `MATHEMATICAL_BASELINE.md`
- `BASELINE_REVISION_NOTES.md`
- `MIXED_SYSTEM_BASELINE.md`
- `VERSION_3_NOTES.md`
- `VERSION_4_NOTES.md`
- `VERSION_4_1_NOTES.md`
- `CAPACITY_COMPOSITION_MODEL.md`

These are useful for understanding which assumptions and corrections entered at each stage.

---

## Citation and provenance

This code originated from an ESGI 195 study of stability measures for inverter-dominated grids and was subsequently corrected and extended into the present reduced SG–GFM–GFL capacity-composition model.

If the repository is used in academic work, please cite the associated ESGI report once its final bibliographic details are fixed.

---

## Licence

This software is released under the MIT License.
