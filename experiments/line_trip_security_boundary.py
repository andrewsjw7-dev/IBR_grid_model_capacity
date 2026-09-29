"""Refine the SG-share security boundary for the diagonal-line outage.

Path: rho_gfm = rho_gfl = (1-rho_sg)/2.
Two distinct boundaries are reported:
1. instantaneous post-trip algebraic solvability at the pre-trip state;
2. transient survival for 4 s after the exact trip.
"""
import numpy as np
from scipy.optimize import least_squares
from experiments.capacity_composition_map import solve_capacity_equilibrium
from experiments.dynamic_capacity_disturbances import run_one


def post_trip_min_residual(rho_sg):
    r=(1-rho_sg)/2
    grid,devices,buses,ratings,dispatch,steady,status=solve_capacity_equilibrium(rho_sg,r,r)
    x=steady.state; Vpre=grid.algebraic_solution(x)
    grid.lines[2].in_service=False; grid.update_network(); net=grid.network; n=len(net.buses)
    def comp(bus,Vbus): return sum(grid._device_current(d,Vbus,x) for d in bus.devices)-grid._load_current(bus,Vbus)
    def unpack(y): return y[:n]+1j*y[n:]
    def residual(y):
        V=unpack(y); Inet=net.Ybus@V; rr=np.array([comp(b,V[i])-Inet[i] for i,b in enumerate(net.buses)])
        return np.r_[rr.real,rr.imag]
    Vp=np.array([Vpre[b] for b in net.buses]); seeds=[np.r_[Vp.real,Vp.imag]]
    for mag in [0.4,0.6,0.8,1.0,1.2]: seeds.append(np.r_[np.full(n,mag),np.zeros(n)])
    best=np.inf
    for y0 in seeds:
        sol=least_squares(residual,y0,max_nfev=3000,xtol=1e-12,ftol=1e-12,gtol=1e-12)
        best=min(best,float(np.linalg.norm(residual(sol.x),np.inf)))
    return best


def bisect_algebraic(lo=0.525,hi=0.55,tol=2.5e-5):
    while hi-lo>tol:
        mid=(lo+hi)/2
        if post_trip_min_residual(mid)<1e-7: lo=mid
        else: hi=mid
    return lo,hi


def dynamic_survives(rho_sg):
    r=(1-rho_sg)/2
    out=run_one(rho_sg,r,r,'line_trip',t_end=4.0)
    return bool(out.get('dynamic_success')),out


def bisect_dynamic(lo=0.50,hi=0.505,tol=1e-4):
    # lo known surviving, hi known failing for current benchmark.
    while hi-lo>tol:
        mid=(lo+hi)/2; ok,_=dynamic_survives(mid)
        if ok: lo=mid
        else: hi=mid
    return lo,hi


if __name__=='__main__':
    a=bisect_algebraic(); d=bisect_dynamic()
    print(f'instantaneous_post_trip_algebraic_boundary_rho_sg in [{a[0]:.8f}, {a[1]:.8f}]')
    print(f'transient_survival_boundary_rho_sg in [{d[0]:.8f}, {d[1]:.8f}]')
    for x in [d[0],d[1],a[0],a[1]]:
        r=(1-x)/2; out=run_one(x,r,r,'line_trip',t_end=4.0)
        print(x,out.get('dynamic_success'),out.get('failure_class'),out.get('failure_time_s'),out.get('minimum_bus_voltage_pu'))
