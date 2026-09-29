"""Capacity-replacement map on the SG/GFM/GFL composition simplex."""
from __future__ import annotations
import csv
from pathlib import Path
import numpy as np
from controls.droop import DroopController
from controls.voltage_droop import VoltageDroopController
from models.bus import Bus
from models.grid import Grid
from models.grid_following_inverter import GridFollowingInverter
from models.grid_forming_inverter import GridFormingInverter
from models.line import Line
from models.load import Load
from models.synchronous_generator import SynchronousGenerator
from simulation.steady_state import SteadyStateSolver
F0=50.0; OMEGA0=2*np.pi*F0; S_BASE=1.0; TOTAL_INSTALLED_RATING=2.0; TOTAL_ACTIVE_LOAD=1.50; TOTAL_REACTIVE_LOAD=0.35; GFL_Q_OVER_P=0.25
H_SG=5.0; D_SG_DEVICE=10.0; XD_SG_DEVICE=0.20; E_SG=1.05
H_GFM=2.5; D_GFM_DEVICE=8.0; X_GFM_DEVICE=0.15; KP_GFM_DEVICE=0.10; KQ_GFM_DEVICE=0.06; V0_GFM=1.03; TAU_E_GFM=0.08; IMAX_GFM_DEVICE=3.0
IMAX_GFL_DEVICE=2.0; KP_PLL=30.0; KI_PLL=200.0; RHO_EPS=1e-10

def _normalise_composition(a,b,c):
    r=np.array([a,b,c],float)
    if np.any(r<-1e-12): raise ValueError("Composition fractions must be non-negative.")
    r[np.abs(r)<1e-12]=0
    if abs(r.sum()-1)>1e-10: raise ValueError("rho_sg + rho_gfm + rho_gfl must equal 1.")
    return r/r.sum()

def build_capacity_system(rho_sg,rho_gfm,rho_gfl):
    rho_sg,rho_gfm,rho_gfl=_normalise_composition(rho_sg,rho_gfm,rho_gfl)
    bsg=Bus("SG_bus"); bgfm=Bus("GFM_bus"); bgfl=Bus("GFL_bus"); grid=Grid(S_base=S_BASE)
    for b in (bsg,bgfm,bgfl): grid.add_bus(b)
    grid.add_line(Line(bsg,bgfm,0.25)); grid.add_line(Line(bgfm,bgfl,0.30)); grid.add_line(Line(bsg,bgfl,0.30))
    grid.add_load(Load("Load_GFM_bus",P=0.35,Q=0.10),bgfm); grid.add_load(Load("Load_GFL_bus",P=1.15,Q=0.25),bgfl)
    ratings={"sg":rho_sg*TOTAL_INSTALLED_RATING,"gfm":rho_gfm*TOTAL_INSTALLED_RATING,"gfl":rho_gfl*TOTAL_INSTALLED_RATING}
    dispatch={"sg":rho_sg*TOTAL_ACTIVE_LOAD,"gfm":rho_gfm*TOTAL_ACTIVE_LOAD,"gfl":rho_gfl*TOTAL_ACTIVE_LOAD}
    devices={}; buses={"sg":bsg,"gfm":bgfm,"gfl":bgfl}
    if rho_sg>RHO_EPS:
        d=SynchronousGenerator("SG",H=H_SG,D=D_SG_DEVICE,Pm=dispatch["sg"],omega0=OMEGA0,E_internal=E_SG,Xd_prime=XD_SG_DEVICE,Sr=ratings["sg"],S_base=S_BASE)
        grid.add_device(d,bsg); devices["sg"]=d
    if rho_gfm>RHO_EPS:
        rp=ratings["gfm"]/S_BASE; pc=DroopController(P0=dispatch["gfm"],kp=KP_GFM_DEVICE*rp,omega0=OMEGA0); qc=VoltageDroopController(V0=V0_GFM,Q0=0.0,kq=KQ_GFM_DEVICE/rp)
        d=GridFormingInverter("GFM",Hv=H_GFM,Dv=D_GFM_DEVICE,omega0=OMEGA0,power_controller=pc,voltage_controller=qc,tauE=TAU_E_GFM,Imax=IMAX_GFM_DEVICE,X_filter=X_GFM_DEVICE,Sr=ratings["gfm"],S_base=S_BASE)
        grid.add_device(d,bgfm); devices["gfm"]=d
    if rho_gfl>RHO_EPS:
        d=GridFollowingInverter("GFL",Pref=dispatch["gfl"],Qref=GFL_Q_OVER_P*dispatch["gfl"],omega0=OMEGA0,Imax=IMAX_GFL_DEVICE,Kp_pll=KP_PLL,Ki_pll=KI_PLL,Sr=ratings["gfl"],S_base=S_BASE)
        grid.add_device(d,bgfl); devices["gfl"]=d
    grid.initialise(); return grid,devices,buses,ratings,dispatch

def solve_capacity_equilibrium(a,b,c):
    grid,devices,buses,ratings,dispatch=build_capacity_system(a,b,c)
    if "sg" not in devices and "gfm" not in devices: return grid,devices,buses,ratings,dispatch,None,"no_voltage_forming_reference"
    x=grid.initial_state()
    if "gfm" in devices: sl=grid.device_state_indices[devices["gfm"]]; x[sl.start+2]=V0_GFM
    gauge={"SG_delta":0.0} if "sg" in devices else {"GFM_delta":0.0}
    steady=SteadyStateSolver(grid,fixed_states=gauge,tolerance=2e-11,max_nfev=5000).solve(x)
    return grid,devices,buses,ratings,dispatch,steady,"solved"

def linearised_jacobian(grid,x):
    x=np.asarray(x,float); n=len(x); J=np.zeros((n,n))
    for j in range(n):
        name=grid.state_names[j]; h=1e-5 if "omega" in name else (1e-7 if name.endswith("_xi") else 1e-6)
        xp=x.copy(); xm=x.copy(); xp[j]+=h; xm[j]-=h; grid._voltage_guess=None; fp=grid.derivatives(0,xp); grid._voltage_guess=None; fm=grid.derivatives(0,xm); J[:,j]=(fp-fm)/(2*h)
    return J

def analyse_composition(a,b,c):
    a,b,c=_normalise_composition(a,b,c); base={"rho_sg":float(a),"rho_gfm":float(b),"rho_gfl":float(c),"grid_forming_fraction":float(a+b),"S_total":TOTAL_INSTALLED_RATING,"P_load":TOTAL_ACTIVE_LOAD}
    try: grid,devices,buses,ratings,dispatch,steady,status=solve_capacity_equilibrium(a,b,c)
    except Exception as exc: return base|{"status":"solve_exception","message":str(exc),"equilibrium_valid":False,"capacity_feasible":False,"locally_stable":False}
    for n in ("sg","gfm","gfl"): base[f"Sr_{n}"]=float(ratings[n]); base[f"Pset_{n}"]=float(dispatch[n])
    if steady is None: return base|{"status":status,"message":status,"equilibrium_valid":False,"capacity_feasible":False,"locally_stable":False}
    try:
        x=steady.state; d=grid.operating_point_diagnostics(x); V=d["bus_voltages"]; powers=d["device_powers"]
        valid=bool(steady.success and steady.max_differential_residual<1e-7 and steady.max_kcl_residual<1e-8 and abs(d["active_power_balance"])<1e-8 and abs(d["reactive_balance_residual"])<1e-8)
        loading={n:np.nan for n in ("sg","gfm","gfl")}; currents=loading.copy(); margins={"gfm":np.nan,"gfl":np.nan}
        for n,dev in devices.items():
            loading[n]=abs(powers[dev])/ratings[n]; st=grid.get_device_state(x,dev); currents[n]=abs(dev.current_injection(V[buses[n]],st))
            if n in margins: margins[n]=dev.Imax-currents[n]
        feasible=valid and all(np.isnan(loading[n]) or loading[n]<=1+1e-7 for n in loading) and all(np.isnan(margins[n]) or margins[n]>=-1e-8 for n in margins)
        eig=np.linalg.eigvals(linearised_jacobian(grid,x)); zi=int(np.argmin(np.abs(eig))); rot=eig[zi]; nt=np.delete(eig,zi)
        if len(nt): crit=nt[np.argmax(nt.real)]; maxreal=float(np.max(nt.real)); stable=maxreal<-1e-6; zeta=float(-crit.real/abs(crit)) if abs(crit)>0 else np.nan; fm=float(abs(crit.imag)/(2*np.pi))
        else: crit=np.nan+1j*np.nan; maxreal=-np.inf; stable=True; zeta=np.nan; fm=np.nan
        out=base|{"status":"ok" if valid else "residual_failure","message":steady.message,"equilibrium_valid":valid,"capacity_feasible":bool(feasible),"locally_stable":bool(valid and stable),"nfev":steady.nfev,"max_differential_residual":steady.max_differential_residual,"max_kcl_residual":steady.max_kcl_residual,"active_power_balance":d["active_power_balance"],"reactive_balance_residual":d["reactive_balance_residual"],"min_bus_voltage_pu":float(min(abs(v) for v in V.values())),"max_bus_voltage_pu":float(max(abs(v) for v in V.values())),"rotational_eigenvalue_abs":float(abs(rot)),"critical_eigenvalue_real":float(np.real(crit)),"critical_eigenvalue_imag":float(np.imag(crit)),"critical_mode_frequency_hz":fm,"critical_damping_ratio":zeta,"max_nontrivial_real_part":maxreal}
        for n in ("sg","gfm","gfl"): out[f"loading_{n}"]=float(loading[n]); out[f"current_{n}"]=float(currents[n])
        out["gfm_current_margin"]=float(margins["gfm"]); out["gfl_current_margin"]=float(margins["gfl"])
        out["Hsys_sg"]=float(devices["sg"].H_system) if "sg" in devices else 0.0; out["Xsys_sg"]=float(devices["sg"].Xd_prime) if "sg" in devices else np.nan
        out["Hsys_gfm"]=float(devices["gfm"].Hv_system) if "gfm" in devices else 0.0; out["Xsys_gfm"]=float(devices["gfm"].X_filter) if "gfm" in devices else np.nan
        return out
    except Exception as exc: return base|{"status":"analysis_exception","message":str(exc),"equilibrium_valid":False,"capacity_feasible":False,"locally_stable":False}

def simplex_points(step=0.025):
    n=int(round(1/step));
    if abs(n*step-1)>1e-12: raise ValueError("step must divide 1 exactly")
    for i in range(n+1):
        for j in range(n+1-i): yield i/n,j/n,(n-i-j)/n

def run_map(step=0.025,csv_path=None,verbose=False):
    rows=[analyse_composition(*p) for p in simplex_points(step)]
    if csv_path:
        fields=[]
        for r in rows:
            for k in r:
                if k not in fields: fields.append(k)
        with Path(csv_path).open('w',newline='') as f: w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    return rows

def summarise(rows):
    valid=[r for r in rows if r.get("equilibrium_valid")]; feasible=[r for r in valid if r.get("capacity_feasible")]; stable=[r for r in feasible if r.get("locally_stable")]; unstable=[r for r in feasible if not r.get("locally_stable")]; no_ref=[r for r in rows if r.get("status")=="no_voltage_forming_reference"]; failures=[r for r in rows if not r.get("equilibrium_valid") and r not in no_ref]
    out={"n_total":len(rows),"n_valid":len(valid),"n_feasible":len(feasible),"n_stable_feasible":len(stable),"n_unstable_feasible":len(unstable),"n_no_voltage_forming_reference":len(no_ref),"n_other_failures":len(failures)}
    if feasible: out["least_stable_feasible"]=max(feasible,key=lambda r:r["max_nontrivial_real_part"]); out["min_grid_forming_fraction_feasible"]=min(r["grid_forming_fraction"] for r in feasible)
    return out
if __name__=="__main__":
    rows=run_map(0.025,"ibr_capacity_composition_map_0025.csv"); print(summarise(rows))
