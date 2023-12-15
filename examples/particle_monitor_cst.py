#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 20:40:31 2023.

@author: placais

This script showcases how the Particle Monitor files from CST can be studied.

"""
from pathlib import Path

import matplotlib.pyplot as plt
from stl import mesh

from multipactor.particle_monitor.particle_monitor import ParticleMonitor
from multipactor.particle_monitor.studies import (
    plot_emission_energies,
    plot_collision_energies,
    plot_trajectories,
    plot_impact_angles,
)

# study_case = 'tesla'
study_case = 'WR75'

if study_case == 'tesla':
    folder, delimiter = Path("cst", "Particle_Monitor", "tesla_no_mp"), None
    stl_file = Path("cst", "Particle_Monitor", "tesla.stl")

elif study_case == 'WR75':
    folder, delimiter = Path("cst", "WR75_reduced", "Export", "3d"), None
    stl_file = Path("cst", "WR75_reduced", "wr75.stl")

else:
    raise IOError(f"{study_case = } not defined.")

if __name__ == '__main__':
    plt.close('all')
    my_particles = ParticleMonitor(folder, delimiter=delimiter)
    my_mesh = mesh.Mesh.from_file(stl_file)

    plot_emission_energies(my_particles, bins=1000, hist_range=(0., 1e2))
    plot_collision_energies(my_particles, bins=1000, hist_range=(0., 2e2))

    pid_to_plot = [i for i in range(100)]
    plot_trajectories(my_particles, pid_to_plot)

    plot_impact_angles(my_particles, my_mesh)
