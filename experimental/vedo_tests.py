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
                                 indexes: int | slice,
                                 ) -> list[Particle]:
    """Give Particle objects corresponding to ``indexes``."""
    parts = list(particle_monitor.values())[indexes]
    if isinstance(parts, Particle):
        return [parts]
    return parts


def _create_trajectory_line(particle: Particle) -> vedo.Lines:
    """Create the plot lines."""
    lines = vedo.Lines(start_pts=particle.pos[:-1],
                       end_pts=particle.pos[1:],
                       lw=7,
                       )
    return lines


def _create_collision_point(particle: Particle) -> vedo.Points:
    """Create a collision point."""
    collision_point = vedo.Point(pos=particle.pos[-1],
                                 r=12,
                                 )
    return collision_point


def _create_extrapolated_position_point(particle: Particle) -> vedo.Points:
    """Create point object corresponding to extrapolated position."""
    assert particle.extrapolated_pos is not None
    extrapolated_point = vedo.Point(pos=particle.extrapolated_pos[-1],
                                    r=8,
                                    c='blue',
                                    )
    return extrapolated_point


def collision_study(particles: list[Particle],
                    structure: vedo.Mesh,
                    add_extrapolated_position: bool = True,
                    ) -> tuple[list[vedo.Lines], list[vedo.Points], Any]:
    """Create trajectory and collision point objects for all particles."""
    trajectories = [_create_trajectory_line(particle)
                    for particle in particles]

    collision_color = (255, 125, 255, 255)
    collision_ids = [find_collision_cell(particle,
                                         structure,
                                         collision_color=collision_color)
                     for particle in particles]

    # Last known point
    collision_points = [_create_collision_point(particle)
                        for particle in particles]
    # tmp add extrapolated position point
    if add_extrapolated_position:
        extrapolated_points = [_create_extrapolated_position_point(particle)
                               for particle in particles]
        collision_points += extrapolated_points

    return trajectories, collision_points, collision_ids


def find_collision_cell(
        particle: Particle,
        structure: vedo.Mesh,
        collision_color: tuple[float, float, float, float] | None = None,
        warn_no_collision: bool = True,
        warn_multiple_collisions: bool = True,
) -> Any:
    """Find where the trajectory impacts the structure."""
    p_0 = particle.pos[-1]
    assert particle.extrapolated_pos is not None
    p_1 = particle.extrapolated_pos[-1]

    intersecting_points, cell_ids = structure.intersect_with_line(
        p0=p_0,
        p1=p_1,
        return_ids=True,
        tol=0)

    if intersecting_points.shape[0] == 0:
        p_1 = p_0
        p_0 = particle.pos[-2]
        intersecting_points, cell_ids = structure.intersect_with_line(
            p0=p_0,
            p1=p_1,
            return_ids=True,
            tol=0)

    if warn_no_collision and intersecting_points.shape[0] == 0:
        print(f"No collision for particle {particle.particle_id}.")
        return cell_ids

    if warn_multiple_collisions and intersecting_points.shape[0] > 1:
        print(f"More than one collision for particle {particle.particle_id}."
              "Only considering the first.")
        intersecting_points = intersecting_points[0]
        cell_ids = cell_ids[0]

    if collision_color is not None:
        my_mesh.cellcolors[cell_ids] = collision_color
    return cell_ids


if __name__ == '__main__':
    vedo.close()
    veplot = vedo.Plotter()

    # basepath = Path("..", "examples", "cst", "WR75_reduced")
    # stl_file = Path(basepath, "wr75.stl")
    # folder, delimiter = Path(basepath, "Export", "3d"), None
    basepath = Path("/", "home", "placais", "Documents", "Projects", "FCC",
                    "2023.12_particle_monitor_studies", "data")
    stl_file = Path(basepath, "swell_1.3GHz_vacuum.stl")
    folder, delimiter = Path(basepath, "5_MV_per_m"), None

    # Set up mesh visualisation
    my_mesh = vedo.load(str(stl_file)).alpha(0.5)
    veplot += my_mesh

    # Set up trajectories visualisation
    my_particle_monitor = ParticleMonitor(folder, delimiter=delimiter)
    to_study = monitor_to_list_of_particles(my_particle_monitor, slice(0, 10))
    to_study = [part for part in to_study
                if not part.alive_at_end]

    trajectories, collision_points, _ = collision_study(
        to_study,
        my_mesh,
        add_extrapolated_position=True)
    veplot += trajectories + collision_points

    # Find intersections
    # my_mesh.intersect_with_lines

    veplot.show()
