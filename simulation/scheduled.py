"""Piecewise integration for exact scheduled network/load switching events."""
from dataclasses import dataclass
import numpy as np
from scipy.integrate import solve_ivp
@dataclass
class ScheduledResult:
    t: np.ndarray
    x: np.ndarray
    success: bool
    message: str
    failure_time: float | None = None
    def final_state(self): return self.x[:,-1].copy()
class ScheduledSimulation:
    def __init__(self,model,events,t_start=0.0,t_end=10.0,dt_output=0.005,method="RK45",rtol=1e-8,atol=1e-10):
        self.model=model; self.events=sorted(list(events),key=lambda e:e.event_time)
        self.t_start=float(t_start); self.t_end=float(t_end); self.dt_output=float(dt_output)
        self.method=method; self.rtol=rtol; self.atol=atol
    def _reset(self):
        for event in self.events:
            try: event.reset(self.model)
            except TypeError: event.reset()
        if hasattr(self.model,"update_network"): self.model.update_network()
        if hasattr(self.model,"_voltage_guess"): self.model._voltage_guess=None
    def run(self,x0):
        self._reset(); xcur=np.asarray(x0,dtype=float).copy(); times=[]; states=[]; current=self.t_start
        groups={}
        for e in self.events:
            if self.t_start<e.event_time<=self.t_end: groups.setdefault(float(e.event_time),[]).append(e)
        boundaries=sorted(groups)+[self.t_end]
        for boundary in boundaries:
            if boundary>current+1e-14:
                n=max(2,int(np.ceil((boundary-current)/self.dt_output))+1); teval=np.linspace(current,boundary,n)
                last={"t":current}
                def rhs(t,x): last["t"]=float(t); return self.model.derivatives(t,x)
                try:
                    sol=solve_ivp(rhs,(current,boundary),xcur,t_eval=teval,method=self.method,rtol=self.rtol,atol=self.atol)
                except Exception as exc:
                    return ScheduledResult(np.asarray(times),np.asarray(states).T if states else np.empty((len(xcur),0)),False,str(exc),float(last["t"]))
                if not sol.success:
                    return ScheduledResult(np.asarray(times),np.asarray(states).T if states else np.empty((len(xcur),0)),False,sol.message,float(sol.t[-1]) if len(sol.t) else current)
                start=0 if not times else 1; times.extend(sol.t[start:].tolist()); states.extend(sol.y[:,start:].T.tolist())
                xcur=sol.y[:,-1].copy(); current=boundary
            elif not times:
                times.append(current); states.append(xcur.tolist())
            if boundary in groups:
                for e in groups[boundary]: e.apply_exact(self.model)
                if hasattr(self.model,"algebraic_solution"):
                    self.model._voltage_guess=None
                    try: self.model.algebraic_solution(xcur)
                    except Exception as exc:
                        return ScheduledResult(np.asarray(times,dtype=float),np.asarray(states,dtype=float).T,False,str(exc),float(boundary))
        return ScheduledResult(np.asarray(times,dtype=float),np.asarray(states,dtype=float).T,True,"success",None)
