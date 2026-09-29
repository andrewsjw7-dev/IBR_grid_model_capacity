"""
Generic simulation engine.

The solver knows nothing about
    - SGs
    - GFMs
    - GFLs
    - Networks

It only solves

        dx/dt = f(t,x)

provided by a model object.
"""

import numpy as np

from scipy.integrate import solve_ivp
from simulation.results import Results


class Simulation:

    def __init__(
            self,
            model,
            t_start=0.0,
            t_end=20.0,
            n_points=2000,
            method="RK45",
            rtol=1e-8,
            atol=1e-10):

        self.model = model

        self.t_start = t_start

        self.t_end = t_end

        self.n_points = n_points

        self.method = method

        self.rtol = rtol

        self.atol = atol


    def run(self, x0):

        t_eval = np.linspace(
            self.t_start,
            self.t_end,
            self.n_points
        )

        solution = solve_ivp(

            fun=self.model.derivatives,

            t_span=(
                self.t_start,
                self.t_end
            ),

            y0=x0,

            t_eval=t_eval,

            method=self.method,

            rtol=self.rtol,

            atol=self.atol

        )

        if not solution.success:

            raise RuntimeError(
                solution.message
            )

        return Results(
            solution,
            self.model
        )
    
    def summary(self):

        print("Simulation")
    
        print("----------------")
    
        print(f"Start : {self.t_start}")
    
        print(f"End   : {self.t_end}")
    
        print(f"Points: {self.n_points}")
    
        print(f"Solver: {self.method}")
    
@property
def duration(self):

    return self.t_end-self.t_start