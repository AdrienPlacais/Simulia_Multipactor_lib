#!/usr/bin/env python3
"""Define a MP study with SPARK3D results."""

from pathlib import Path

import numpy as np

from simultipac.simulation_results.simulations_results import (
    SimulationsResults,
    SimulationsResultsFactory,
)

if __name__ == "__main__":
    factory = SimulationsResultsFactory("SPARK3D", freq_ghz=1.30145)
    results: SimulationsResults = factory.create(
        filepath=Path("spark/time_results.csv"),
        e_acc=np.linspace(1e6, 3e7, 30),
    )
    idx_to_plot = (0, 15, 25)
    axes = results.plot(
        x="time", y="population", idx_to_plot=idx_to_plot, alpha=0.7
    )

    results.fit_alpha(fitting_periods=20)
    results.plot(
        x="time",
        y="modelled_population",
        idx_to_plot=idx_to_plot,
        axes=axes,
        lw=3,
        ls="--",
    )
    axes.set_yscale("log")
    results.plot(x="e_acc", y="alpha", idx_to_plot=range(0, 5))

    # Sometimes necessary to show the plots, eg when running script from bash
    results.show()
