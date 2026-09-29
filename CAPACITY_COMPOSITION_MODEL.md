# Capacity-composition baseline (Version 4)

Version 4 distinguishes installed capacity from active-power dispatch.  The
fixed system base is `S_base`, and each aggregate SG/GFM/GFL device has a
rating `Sr`.  Composition fractions satisfy

\[
\rho_{\rm SG}+\rho_{\rm GFM}+\rho_{\rm GFL}=1,
\qquad
S_{r,i}=\rho_i S_{\rm total}.
\]

The benchmark uses `S_base=1 pu`, total installed rating `S_total=2 pu`, and
fixed active load `P_L=1.5 pu`.  Active dispatch is proportional to installed
capacity, so every technology is nominally at 75% active loading before
reactive-power requirements are included.

## Common-base conversion

For an SG whose inertia constant H and transient reactance Xd' are specified
on its own rating base,

\[
H_{\rm sys}=H\frac{S_r}{S_B},
\qquad
M_{\rm sys}=\frac{2HS_r}{\omega_0S_B},
\]

and

\[
X'_{d,\rm sys}=X'_{d,\rm dev}\frac{S_B}{S_r}.
\]

The damping-power coefficient is converted as

\[
D_{\rm sys}=D_{\rm dev}\frac{S_r}{S_B}.
\]

The same inertia, damping and reactance conversion is used for the GFM.  GFM
and GFL current limits are specified on the device base and converted to the
system base as

\[
I_{\max,\rm sys}=I_{\max,\rm dev}\frac{S_r}{S_B}
\]

for a common voltage base.

For the capacity map, the GFM P-droop gain is treated as a device-base power
coefficient and therefore scales with rating,

\[
k_{p,\rm sys}=k_{p,\rm dev}\frac{S_r}{S_B},
\]

whereas its Q-V slope, when Q is supplied on the system base, scales as

\[
k_{q,\rm sys}=k_{q,\rm dev}\frac{S_B}{S_r}.
\]

The GFL has no inertia, but it has an explicit rating so that its current
capability also scales with installed capacity.

## Boundary handling

A technology with exactly zero rating is removed from the dynamic model rather
than creating a singular zero-inertia state.  An island containing only GFL
current-source devices has no voltage-forming reference and is therefore
classified as `no_voltage_forming_reference`; Version 4 does not hide this by
adding an artificial slack/infinite bus.

## Composition-map tests

Each composition point is required to satisfy the steady reduced DAE to tight
residual tolerances.  The code then checks apparent-power rating, converter
current limits, and the eigenvalues of the algebraically reduced differential
Jacobian after removing the one rotational-symmetry eigenvalue.

The distributed load and three-bus network are unchanged from Version 3.
