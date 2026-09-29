"""Exactly scheduled permanent constant-PQ load step."""
from disturbances.disturbance import Disturbance
class LoadStep(Disturbance):
    def __init__(self, load, step_time, delta_P=0.0, delta_Q=0.0):
        super().__init__(start_time=step_time, end_time=None, name="LoadStep")
        self.load=load; self.step_time=float(step_time); self.delta_P=float(delta_P); self.delta_Q=float(delta_Q)
        self._P0=float(load.P); self._Q0=float(load.Q)
    @property
    def event_time(self): return self.step_time
    def check(self,t): return (not self.applied) and t>=self.step_time
    def apply(self,t,grid):
        if not self.check(t): return
        self.load.P=self._P0+self.delta_P; self.load.Q=self._Q0+self.delta_Q
        grid._voltage_guess=None; self.applied=True
    def apply_exact(self,grid): self.apply(self.step_time,grid)
    def reset(self,grid=None):
        self.load.P=self._P0; self.load.Q=self._Q0; self.applied=False; self.cleared=False
        if grid is not None: grid._voltage_guess=None
    def __repr__(self): return f"LoadStep({self.load.name}, t={self.step_time}, dP={self.delta_P}, dQ={self.delta_Q})"
