#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 23 13:40:42 2023.

@author: placais

.. todo::
    histogram impacts

"""
from pathlib import Path
import random

import vedo

from multipactor.particle_monitor.studies import plot_impact_angles
from multipactor.particle_monitor.particle import Particle
from multipactor.particle_monitor.particle_monitor import ParticleMonitor
from multipactor.visualization.plot_3d import (
    plot_structure_and_some_trajectories
)


def monitor_to_list_of_particles(particle_monitor: ParticleMonitor,
                                 indexes: int | slice,
                                 ) -> list[Particle]:
    """Give Particle objects corresponding to ``indexes``."""
    parts = list(particle_monitor.values())[indexes]
    if isinstance(parts, Particle):
        return [parts]
    return parts



if __name__ == '__main__':
    vedo.close()

    # basepath = Path("..", "examples", "cst", "WR75_reduced")
    # stl_file = Path(basepath, "wr75.stl")
    # folder, delimiter = Path(basepath, "Export", "3d"), None
    basepath = Path("/", "home", "placais", "Documents", "Projects", "FCC",
                    "2023.12_particle_monitor_studies", "data")
    stl_file = Path(basepath, "swell_1.3GHz_vacuum.stl")
    folder, delimiter = Path(basepath, "5_MV_per_m"), None

    my_mesh = vedo.load(str(stl_file)).alpha(0.5)

    my_particle_monitor = ParticleMonitor(folder, delimiter=delimiter)
    max_pid = max(list(my_particle_monitor.keys()))
    number_of_particles_to_plot = 5
    pid_to_plot = random.sample(list(my_particle_monitor.keys()),
                                number_of_particles_to_plot)

    plot_structure_and_some_trajectories(
        my_particle_monitor,
        pid_to_plot,
        my_mesh,
    )

    # %%
    plot_impact_angles(my_particle_monitor, my_mesh)
    # # Find intersections
    # # my_mesh.intersect_with_lines

    # veplot.show()
    # if collision_color is not None:
    #     my_mesh.cellcolors[cell_ids] = collision_color
    # return cell_ids
