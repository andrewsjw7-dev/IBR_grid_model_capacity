"""Exactly timed load-step and line-trip tests along a capacity-replacement path."""
from __future__ import annotations
import csv
from pathlib import Path
import numpy as np
from disturbances.load_step import LoadStep
from disturbances.line_trip import LineTrip
from experiments.capacity_composition_map import OMEGA0, analyse_composition, solve_capacity_equilibrium
from simulation.scheduled import ScheduledSimulation
F0=OMEGA0/(2*np.pi); EVENT_TIME=1.0

def _wrap(a): return np.angle(np.exp(1j*a))
def _metrics(grid,devices,buses,steady,result):
    t=result.t; X=result.x; post=t>=EVENT_TIME-1e-12; f=np.array([grid.centre_of_inertia_frequency(X[:,k])/(2*np.pi) for k in range(X.shape[1])]); fp=f[post]; tp=t[post]
    ro=np.gradient(fp,tp) if len(tp)>2 else np.array([np.nan]); mro=float(np.max(np.abs(ro[tp<=EVENT_TIME+1.0]))) if len(tp)>2 else np.nan
    minv=np.inf; glim=False; flim=False; gr=[]; fr=[]; rels=[]; plls=[]
    rel0=None
    if "sg" in devices and "gfm" in devices:
        ss=grid.device_state_indices[devices["sg"]]; sf=grid.device_state_indices[devices["gfm"]]; rel0=steady.state[sf.start]-steady.state[ss.start]
    idx=np.unique(np.r_[np.arange(0,X.shape[1],4),X.shape[1]-1]); grid._voltage_guess=None
    for k in idx:
        x=X[:,k]; V=grid.algebraic_solution(x); minv=min(minv,min(abs(v) for v in V.values()))
        if "gfm" in devices:
            d=devices["gfm"]; st=grid.get_device_state(x,d); q=abs(d.unconstrained_current(V[buses["gfm"]],st))/d.Imax; gr.append(q); glim|=q>1+1e-8
        if "gfl" in devices:
            d=devices["gfl"]; st=grid.get_device_state(x,d); q=abs(d.unconstrained_current(V[buses["gfl"]],st))/d.Imax; fr.append(q); flim|=q>1+1e-8; plls.append(abs(_wrap(st[0]-np.angle(V[buses["gfl"]]))))
        if rel0 is not None: rels.append(abs(_wrap((x[sf.start]-x[ss.start])-rel0)))
    return {"frequency_nadir_hz":float(np.min(fp)),"frequency_zenith_hz":float(np.max(fp)),"max_frequency_deviation_hz":float(np.max(np.abs(fp-F0))),"max_abs_rocof_hz_s_first_1s":mro,"final_coi_frequency_hz":float(f[-1]),"minimum_bus_voltage_pu":float(minv),"max_gfm_unconstrained_current_ratio":float(max(gr)) if gr else np.nan,"max_gfl_unconstrained_current_ratio":float(max(fr)) if fr else np.nan,"gfm_current_limit_activated":bool(glim),"gfl_current_limit_activated":bool(flim),"max_sg_gfm_relative_angle_deviation_rad":float(max(rels)) if rels else np.nan,"max_pll_angle_error_rad":float(max(plls)) if plls else np.nan,"loss_of_synchronism":bool(rels and max(rels)>np.pi),"pll_loss_of_lock":bool(plls and max(plls)>np.pi/2)}

def run_one(a,b,c,disturbance,t_end=8.0):
    st=analyse_composition(a,b,c); base={"rho_sg":a,"rho_gfm":b,"rho_gfl":c,"disturbance":disturbance,"static_equilibrium_valid":st.get("equilibrium_valid",False),"static_capacity_feasible":st.get("capacity_feasible",False),"static_locally_stable":st.get("locally_stable",False),"static_max_real_eigenvalue":st.get("max_nontrivial_real_part",np.nan)}
    if not(st.get("equilibrium_valid") and st.get("capacity_feasible")): return base|{"dynamic_success":False,"dynamic_message":"static point infeasible","failure_class":"static_infeasible"}
    try:
        grid,devices,buses,ratings,dispatch,steady,status=solve_capacity_equilibrium(a,b,c)
        if disturbance=="load_step": event=LoadStep(next(l for l in grid.loads if l.bus is buses["gfl"]),EVENT_TIME,delta_P=0.10,delta_Q=0.02)
        elif disturbance=="line_trip": event=LineTrip(grid.lines[2],EVENT_TIME)
        else: raise ValueError(disturbance)
        result=ScheduledSimulation(grid,[event],t_end=t_end,dt_output=0.005,rtol=2e-8,atol=2e-10).run(steady.state)
        if not result.success:
            fc="post_event_algebraic_infeasible" if result.failure_time is not None and abs(result.failure_time-EVENT_TIME)<1e-9 else ("transient_algebraic_collapse" if result.failure_time is not None and result.failure_time>EVENT_TIME else "integration_failure")
            return base|{"dynamic_success":False,"dynamic_message":result.message,"failure_time_s":result.failure_time,"failure_class":fc}
        return base|{"dynamic_success":True,"dynamic_message":"success","failure_time_s":np.nan,"failure_class":"none"}|_metrics(grid,devices,buses,steady,result)
    except Exception as exc: return base|{"dynamic_success":False,"dynamic_message":str(exc),"failure_time_s":np.nan,"failure_class":"exception"}

def run_replacement_path(csv_path=None):
    rows=[]
    for a in [0.80,0.60,0.40,0.20,0.05]:
        b=c=(1-a)/2
        for d in ["load_step","line_trip"]: rows.append(run_one(a,b,c,d))
    if csv_path:
        fields=[]
        for r in rows:
            for k in r:
                if k not in fields: fields.append(k)
        with Path(csv_path).open('w',newline='') as f: w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    return rows
if __name__=="__main__":
    for r in run_replacement_path("ibr_capacity_dynamic_disturbances.csv"): print(r)
