"""Perform a MP study with CST Particle Monitor.

.. note::
    Here, we look at only one simulation. The object that we create is not a
    :class:`.SimulationsResults`, but a :class:`.SimulationResults`
    (``Simulation`` is singular).

.. todo::
    Currently, only showcases ideal UI. Some things are left to implement.

"""

from collections.abc import Sequence
from pathlib import Path
from typing import Literal

import pandas as pd

from simultipac.cst.simulation_results import CSTResults, CSTResultsFactory
from simultipac.particle_monitor.particle_monitor import ParticleMonitor

if __name__ == "__main__":
    factory = CSTResultsFactory(
        freq_ghz=1.30145,
        stl_path=Path("../docs/manual/data/cst/WR75_reduced/wr75.stl"),
    )

    result: CSTResults = factory._from_simulation_folder(
        # Dummy results that are not related to the actual ParticleMonitor data
        # we will use
        folderpath=Path("./cst/Export_Parametric/0307-5216540"),
        folder_particle_monitor=Path(
            "../docs/manual/data/cst/WR75_reduced/Export/3d"
        ),
    )
    monitor: ParticleMonitor = result._particle_monitor

    monitor.hist("emission_energy", filter="seed", bins=10)
    # part_mon.hist("collision_energy", filter="seed", bins=10)
    # part_mon.hist("collision_angle", filter="seed", bins=10)

    if False:
        result.hist(
            x="emission_energies",
            bins=200,
            hist_range=(0, 1e2),
        )
        result.hist(x="collision_energies", bins=200, hist_range=(0, 2e2))

        # Needs stl to be loaded
        # computing is automatically performed if not already done (@property)
        # result.compute_collision_angles(warn_multiple_collisions=False, warn_no_collision=True)
        result.hist(x="collision_angles", bins=200, hist_range=(0, 90))

        # Needs stl to be loaded
        # to_plot can be a Sequence of PID, or the magic keyword
        result.plot_3d(
            "trajectory", to_plot="random sample", extrapolate_positions=False
        )

        # New features
        result.plot_3d("collision_distribution")
        result.plot_3d("emission_distribution")
