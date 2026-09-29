"""
Test the simulation framework.

Uses a simple exponential decay model:

        dx/dt = -x

whose analytical solution is:

        x(t)=exp(-t)

This tests:
    - DynamicModel
    - Simulation
    - Results
"""


from models.dynamic_model import DynamicModel

from simulation.solver import Simulation



class DecayModel(DynamicModel):


    def __init__(self):

        super().__init__()

        self.state_names = [
            "x"
        ]


    def derivatives(self, t, x):

        return [

            -x[0]

        ]



# --------------------------------------------------
# Create model
# --------------------------------------------------

model = DecayModel()



# --------------------------------------------------
# Create simulation
# --------------------------------------------------

simulation = Simulation(

    model=model,

    t_start=0,

    t_end=5,

    n_points=100

)



simulation.summary()



# --------------------------------------------------
# Run simulation
# --------------------------------------------------

x0 = [

    1.0

]


results = simulation.run(x0)



# --------------------------------------------------
# Inspect results
# --------------------------------------------------

results.summary()


print()

print("First time points:")

print(results.t[:5])


print()

print("First state values:")

print(results["x"][:5])

from simulation.plotter import Plotter


plotter = Plotter(results)


plotter.state(
    "x",
    ylabel="x(t)"
)