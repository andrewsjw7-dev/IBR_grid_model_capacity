from disturbances.line_trip import LineTrip
from disturbances.load_step import LoadStep
from experiments.capacity_composition_map import solve_capacity_equilibrium
from simulation.scheduled import ScheduledSimulation
def test_line_trip_not_early_and_resets():
    grid,devices,buses,ratings,dispatch,steady,status=solve_capacity_equilibrium(.4,.35,.25); line=grid.lines[2]; e=LineTrip(line,1); e.apply(.5,grid); assert line.in_service; e.apply(1,grid); assert not line.in_service; e.reset(grid); assert line.in_service
def test_exact_load_step():
    grid,devices,buses,ratings,dispatch,steady,status=solve_capacity_equilibrium(.4,.35,.25); load=next(l for l in grid.loads if l.bus is buses['gfl']); e=LoadStep(load,.5,delta_P=.02); r=ScheduledSimulation(grid,[e],t_end=.8,dt_output=.02).run(steady.state); assert r.success; assert abs(load.P-1.17)<1e-14; e.reset(grid); assert abs(load.P-1.15)<1e-14
