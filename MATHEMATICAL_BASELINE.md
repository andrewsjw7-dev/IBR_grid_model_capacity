# Corrected mathematical baseline

This version replaces the original "first device defines the bus voltage"
approximation by an algebraic network solution while preserving the original
object-oriented structure and `solve_ivp` differential-state workflow.

## 1. Semi-explicit DAE

The differential state is `x` (SG/GFM/GFL controller states) and the
algebraic state is the complex bus-voltage vector `V`:

\[
\dot x=f(x,V),\qquad 0=g(x,V).
\]

At each ODE RHS evaluation, `Grid.algebraic_solution` solves the KCL equations
for `V`, then evaluates device dynamics. This is an index-1 DAE treated by
algebraic elimination.

For each non-fixed bus \(i\),

\[
0=\sum_{d\in\mathcal D_i} I_{d,i}(V_i,x_d)
   -I_{L,i}(V_i)
   -\sum_jY_{ij}V_j.
\]

An infinite bus fixes its bus phasor exactly and supplies the residual current.

## 2. Constant-PQ load

For positive consumption \(S_L=P_L+jQ_L\),

\[
I_L=\overline{S_L/V}=\frac{P_L-jQ_L}{V^*}.
\]

## 3. Synchronous generator

The SG internal EMF is \(E'e^{j\delta}\) behind \(X'_d\):

\[
I_g=\frac{E'e^{j\delta}-V_i}{jX'_d},\qquad
S_g=V_i I_g^*=P_g+jQ_g.
\]

Preferred conventional inertia form (absolute \(\omega\) in rad/s):

\[
\dot\delta=\omega-\omega_0,
\]

\[
\dot\omega=\frac{\omega_0}{2H}
\left[P_m-P_g-D\frac{\omega-\omega_0}{\omega_0}\right].
\]

The old `M` form remains available only for backwards compatibility.

## 4. Grid-forming inverter

The GFM is an internal controlled voltage \(Ee^{j\delta}\) behind filter or
virtual reactance \(X_f\):

\[
I_f=\frac{Ee^{j\delta}-V_i}{jX_f},\qquad
S_f=V_i I_f^*=P_f+jQ_f.
\]

The current is limited radially to \(|I_f|\le I_{\max}\).

The retained controllers are

\[
P^*=P_0-k_p(\omega-\omega_0),
\]

\[
E^*=V_0-k_q(Q_f-Q_0),
\]

and, with `Hv` supplied,

\[
\dot\delta=\omega-\omega_0,
\]

\[
\dot\omega=\frac{\omega_0}{2H_v}
\left[P^*-P_f-D_v\frac{\omega-\omega_0}{\omega_0}\right],
\]

\[
\tau_E\dot E=E^*-E.
\]

## 5. Grid-following inverter

The GFL no longer imposes a bus voltage. It measures the solved bus phasor.
The SRF-PLL is

\[
v_q=|V_i|\sin(\theta_i-\hat\theta),
\]

\[
\dot\xi=v_q,
\]

\[
\hat\omega=\omega_0+K_pv_q+K_i\xi,
\]

\[
\dot{\hat\theta}=\hat\omega-\omega_0.
\]

The ideal current-controller baseline commands

\[
I_\ell^*=\frac{P_{\rm ref}-jQ_{\rm ref}}{V_i^*},
\]

with radial saturation \(|I_\ell|\le I_{\max}\).

## 6. Exact validation problems

Run

```bash
python -m validation.baseline_validations
```

The script checks:

1. SG behind \(X'_d\) and a line connected to an infinite bus. The exact
   equilibrium uses
   \[
   P_m=\frac{E'V_\infty}{X'_d+X_\ell}\sin\delta^*.
   \]
2. GFM behind \(X_f\) and a line connected to an infinite bus. The active
   equilibrium has the same series-reactance power-angle relation; \(Q_0\) is
   chosen from the exact terminal complex power so the voltage-droop state is
   also exactly stationary.
3. GFL directly connected to an infinite bus. The exact PLL equilibrium is
   \(\hat\theta=\theta_\infty,\xi=0\), and the terminal complex power is checked
   against \(P_{\rm ref}+jQ_{\rm ref}\).

Each case also receives a small perturbation and is required to return to the
known stable equilibrium.
