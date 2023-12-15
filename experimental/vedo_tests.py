#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 23 13:40:42 2023.

@author: placais

.. todo::
    histogram impacts

"""
from pathlib import Path
from typing import Any

import vedo

from multipactor.particle_monitor.particle import Particle
from multipactor.particle_monitor.particle_monitor import ParticleMonitor


def monitor_to_list_of_particles(particle_monitor: ParticleMonitor,
                                 indexes: int | slice
                                 ) -> list[Particle]:
    """Give Particle objects corresponding to ``indexes``."""
    parts = list(particle_monitor.values())[indexes]
    if isinstance(parts, Particle):
        return [parts]
    return parts


def create_trajectory_plot_objects(particle: Particle) -> vedo.Lines:
    """Create the plot lines."""
    lines = vedo.Lines(start_pts=particle.pos[:-1],
                       end_pts=particle.pos[1:],
                       lw=7,
                       )
    return lines


def create_collision_point_object(particle: Particle) -> vedo.Points:
    """Create a collision point."""
    collision_point = vedo.Point(pos=particle.pos[-1],
                                 r=12,
                                 )
    return collision_point


def collision_study(particles: list[Particle],
                    structure: vedo.Mesh
                    ) -> tuple[list[vedo.Lines], list[vedo.Points], Any]:
    """Create trajectory and collision point objects for all particles."""
    trajectories = [create_trajectory_plot_objects(particle)
                    for particle in particles]

    collision_color = (255, 125, 255, 255)
    collision_ids = [find_collision_cell(particle,
                                         structure,
                                         collision_color=collision_color)
                     for particle in particles]

    # Last known point
    collision_points = [create_collision_point_object(particle)
                        for particle in particles]

    return trajectories, collision_points, collision_ids


def find_collision_cell(
        particle: Particle,
        structure: vedo.Mesh,
        collision_color: tuple[float, float, float, float] | None = None
) -> Any:
    """Find where the trajectory impacts the structure."""
    # cell = structure.find_cells_along_line(particle.pos[-2],
    #                                        particle.pos[-1],
    #                                        tol=0.01)

    print("extrapolate position maybe")
    collision_id = structure.intersect_with_line(particle.pos[-1],
                                                 particle.pos[-1],
                                                 return_ids=True,
                                                 tol=0)

    if collision_color is not None:
        my_mesh.cellcolors[collision_id] = collision_color
    return collision_id


if __name__ == '__main__':
    vedo.close()
    veplot = vedo.Plotter()

    # basepath = Path("..", "examples", "cst", "WR75_reduced")
    # stl_file = Path(basepath, "wr75.stl")
    # folder, delimiter = Path(basepath, "Export", "3d"), None
    basepath = Path("/", "home", "placais", "Documents", "Projects", "FCC",
                    "2023.12_particle_monitor_studies", "data")
    stl_file = Path(basepath, "swell_1.3GHz.stl")
    folder, delimiter = Path(basepath, "5_MV_per_m"), None

    # Set up mesh visualisation
    my_mesh = vedo.load(str(stl_file)).alpha(0.4)
    veplot += my_mesh

    # Set up trajectories visualisation
    my_particle_monitor = ParticleMonitor(folder, delimiter=delimiter)
    to_study = monitor_to_list_of_particles(my_particle_monitor, slice(0, 10))
    trajectories, collision_points, _ = collision_study(to_study, my_mesh)
    veplot += trajectories + collision_points

    # Find intersections
    # my_mesh.intersect_with_lines

    veplot.show()
