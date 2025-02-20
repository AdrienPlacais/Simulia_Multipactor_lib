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

if __name__ == "__main__":
    factory = CSTResultsFactory(
        "CST",
        freq_ghz=1.30145,
        # Not mandatory. Runs:
        # self.mesh = vedo.load(str(stl_path))
        # self.mesh.alpha(0.3)
        stl_path=Path("../docs/manual/data/cst/WR75_reduced/wr75.stl"),
    )
    result: CSTResults = factory._from_simulation_folder(
        folderpath=Path("../docs/manual/data/cst/WR75_reduced/"),
        particle_monitors=Path("../docs/manual/data/cst/WR75_reduced/"),
    )

    result.hist(x="emission_energies", bins=200, hist_range=(0, 1e2))
    result.hist(x="collision_energies", bins=200, hist_range=(0, 2e2))

    # Needs stl to be loaded
    # computing is automatically performed if not already done (@property)
    # result.compute_collision_angles(warn_multiple_collisions=False, warn_no_collision=True)
    result.hist(x="collision_angles", bins=200, hist_range=(0, 90))

    # Needs stl to be loaded
    # to_plot can be a Sequence of PID, or the magic keyword
    result.plot3d(
        "trajectories", to_plot="random sample", extrapolate_positions=False
    )

    # New features
    result.plot3d("collision_distribution")
    result.plot3d("emission_distribution")
