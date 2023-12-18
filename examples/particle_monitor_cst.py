#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Showcase what we can do with the Particle Monitor files from CST.

Note that the ``vedo`` library must be installed for the
:func:`plot_trajectories` and :func:`plot_collision_angles` functions to work.

.. note::
    According to your configuration, all plots may not appear. For example, you
    may have only the ``matplotlib`` (2D) plots when running this from Spyder.
    Try running this script from the command line to see the ``vedo`` (3D)
    plot.

"""
from pathlib import Path
import random

import matplotlib.pyplot as plt
import vedo

from multipactor.particle_monitor.particle_monitor import ParticleMonitor
from multipactor.particle_monitor.studies import (
    plot_emission_energies,
    plot_collision_angles,
    plot_collision_energies,
)
from multipactor.visualization.plot_3d import (
    plot_structure_and_some_trajectories,
)


if __name__ == '__main__':
    study_case = 'tesla'
    # study_case = 'WR75'

    if study_case == 'tesla':
        folder = Path("cst", "Particle_Monitor", "tesla_no_mp")
        delimiter = None
        stl_file = Path("cst", "Particle_Monitor", "tesla.stl")

    elif study_case == 'WR75':
        folder, delimiter = Path("cst", "WR75_reduced", "Export", "3d"), None
        stl_file = Path("cst", "WR75_reduced", "wr75.stl")

    else:
        raise IOError(f"{study_case = } not defined.")

    plt.close('all')
    particle_monitor = ParticleMonitor(folder, delimiter=delimiter)
    plot_emission_energies(particle_monitor, bins=1000, hist_range=(0., 1e2))
    plot_collision_energies(particle_monitor, bins=1000, hist_range=(0., 2e2))

    mesh = vedo.load(str(stl_file)).alpha(0.3)
    particle_monitor.compute_collision_angles(mesh,
                                              warn_multiple_collisions=False)

    plot_collision_angles(particle_monitor, mesh, bins=100)
    number_of_particles_to_plot = 5
    pid_to_plot = random.sample(list(particle_monitor.keys()),
                                number_of_particles_to_plot)
    plot_structure_and_some_trajectories(particle_monitor,
                                         pid_to_plot,
                                         mesh,
                                         add_extrapolated_position=False,)
