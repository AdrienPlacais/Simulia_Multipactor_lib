#!/usr/bin/env python3
"""Perform a MP study with CST Particle Monitor.

.. note::
    Here, we look at only one simulation. The object that we create is not a
    :class:`.SimulationsResults`, but a :class:`.SimulationResults`
    (``Simulation`` is singular).

.. todo::
    Currently, only showcases ideal UI. Some things are left to implement.

"""

from pathlib import Path

from simultipac.cst.simulation_results import CSTResults, CSTResultsFactory
from simultipac.plotter.default import DefaultPlotter

if __name__ == "__main__":
    # Warning! Default ``vedo_backend`` can lead to crashes or nothing
    # appearing, depending on your interpreter and env
    # For me, this script will not work in Spyder
    plotter = DefaultPlotter(vedo_backend="vtk")
    stl_path = Path("../docs/manual/data/cst/WR75_reduced/wr75.stl")
    factory = CSTResultsFactory(
        plotter=plotter,
        freq_ghz=1.30145,
        stl_path=stl_path,
        stl_alpha=0.3,
    )

    result: CSTResults = factory._from_simulation_folder(
        # Dummy results that are not related to the actual ParticleMonitor data
        # we will use
        folderpath=Path("./cst/Export_Parametric/0307-5216540"),
        folder_particle_monitor=Path(
            "../docs/manual/data/cst/WR75_reduced/Export/3d"
        ),
        load_first_n_particles=10,
    )

    histogram_examples = True
    if histogram_examples:
        # The three types of histograms currently implemented, with some `hist`
        # method arguments examples
        # result.hist("emission_energy", filter="emitted")
        result.hist("collision_energy", filter="seed", hist_range=(0, 100))
        # result.hist("collision_angle", bins=100)
        # TODO : result.hist("emission_angle")

    plots_3d_examples = True
    if plots_3d_examples:
        result.plot_mesh()
        result.plot_trajectories(
            emission_color=None,
            collision_color="red",
            filter=lambda particle: particle.particle_id < 100,
        )

    result.show()
