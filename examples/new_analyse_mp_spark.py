"""Define the interface of the new code."""

from pathlib import Path

import numpy as np

from simultipac.simulation_results.simulations_results import (
    SimulationResultsFactory,
)
from simultipac.spark3d.simulation_results import Spark3DResults

factory = SimulationResultsFactory()
results: Spark3DResults = factory.create(
    tool="SPARK3D",
    filepath=Path("spark/time_results.csv"),
    e_acc=np.linspace(1e6, 3e7, 30),
    freq=1.30145,
)
idx_to_plot = (0, 5, 10)
axes = results.plot(x="time", y="population", idx_to_plot=idx_to_plot)

results.fit_alpha(fitting_periods=20, model="classic")
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
