"""Transmission-line trip with exact scheduled-event support."""
from disturbances.disturbance import Disturbance
class LineTrip(Disturbance):
    def __init__(self,line,trip_time):
        super().__init__(start_time=trip_time,end_time=None,name="LineTrip")
        self.line=line; self.trip_time=float(trip_time); self.triggered=False; self._initial_in_service=bool(line.in_service)
    @property
    def event_time(self): return self.trip_time
    def check(self,t): return (not self.triggered) and t>=self.trip_time
    def apply(self,t,grid):
        if not self.check(t): return
        self.line.in_service=False; grid.update_network(); grid._voltage_guess=None
        self.triggered=True; self.applied=True
    def apply_exact(self,grid): self.apply(self.trip_time,grid)
    def reset(self,grid=None):
        self.line.in_service=self._initial_in_service; self.triggered=False; self.applied=False; self.cleared=False
        if grid is not None: grid.update_network(); grid._voltage_guess=None
    def __repr__(self): return f"LineTrip({self.line}, t={self.trip_time})"
