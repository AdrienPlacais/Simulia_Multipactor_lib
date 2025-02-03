"""Define the interface of the new code."""

from pathlib import Path

from simultipac.cst.simulation_results import CSTResults
from simultipac.simulation_results.simulations_results import (
    SimulationResultsFactory,
)

factory = SimulationResultsFactory()
results: CSTResults = factory.create(
    tool="CST",
    folderpath=Path("cst/Export_Parametric"),
)
idx_to_plot = (0, 5, 10)
axes = results.plot(x="time", y="population", idx_to_plot=idx_to_plot)

results.fit_alpha(fitting_periods=5, model="classic")
results.plot(
    x="time", y="alpha", idx_to_plot=idx_to_plot, same_colors=True, axes=axes
)
results.plot(x="e_acc", y="alpha")
results.save(
    "growth.txt",
    *(
        "e_acc",
        "alpha",
    ),
    delimiter="\t",
)
