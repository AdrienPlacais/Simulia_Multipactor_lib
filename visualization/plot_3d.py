#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Handle 3d visualisation plots with ``vedo`` library."""
from collections.abc import Sequence

import vedo

from multipactor.particle_monitor.particle import Particle
from multipactor.particle_monitor.particle_monitor import ParticleMonitor


def _create_trajectory_line(particle: Particle) -> vedo.Lines:
    """Create the trajectory line object."""
    lines = vedo.Lines(start_pts=particle.pos[:-1],
                       end_pts=particle.pos[1:],
                       lw=7,
                       )
    return lines


def _create_collision_point(particle: Particle) -> vedo.Points | None:
    """Create a collision point if particle not alive at end."""
    if particle.alive_at_end:
        return
    collision_point = vedo.Point(pos=particle.pos[-1],
                                 r=8,
                                 )
    return collision_point


def _create_emission_point(particle: Particle) -> vedo.Points | None:
    """Create a starting green points if particle is an emitted electron."""
    if particle.source_id == 0:
        return
    emission_point = vedo.Point(pos=particle.pos[0],
                                r=8,
                                c='green',
                                )
    return emission_point


def _create_extrapolated_position_point(particle: Particle) -> vedo.Points:
    """Create point object corresponding to extrapolated position."""
    assert particle.extrapolated_pos is not None
    extrapolated_point = vedo.Point(pos=particle.extrapolated_pos[-1],
                                    r=8,
                                    c='blue',
                                    )
    return extrapolated_point


def _create_all_points(particles: list[Particle],
                       add_extrapolated_position: bool
                       ) -> list[vedo.Points]:
    """Call all the Point creation functions."""
    points = [_create_emission_point(particle)
              for particle in particles]
    points += [_create_collision_point(particle)
               for particle in particles]
    if add_extrapolated_position:
        points += [_create_extrapolated_position_point(particle)
                   for particle in particles]

    points = [points for point in points if point is not None]
    return points


def plot_structure_and_some_trajectories(
        particle_monitor: ParticleMonitor,
        pid_to_plot: Sequence,
        mesh: vedo.Mesh,
        veplot: vedo.Plotter | None = None,
        add_extrapolated_position: bool = False,
        **kwargs) -> vedo.Plotter:
    """Create a simple representation of the structure and some trajectories.

    Parameters
    ----------
    particle_monitor : ParticleMonitor
        Dictionary-like structure holding :class:`.Particle` objects.
    pid_to_plot : Sequence
        CST ID of the particles to plot. Corresponds to the
        ``particle_monitor`` keys.
    mesh : vedo.Mesh
        Mesh of the rf system under study. Use :func:``vedo.load`` to create
        it.
    veplot : vedo.Plotter | None, optional
        Object holding the plot. If not provided, a new one is created.
    add_extrapolated_position : bool, optional
        To add a blue point showing where the last of the extrapolated
        positions is. The default is False.
    kwargs :
        kwargs

    """
    if veplot is None:
        veplot = vedo.Plotter()
    assert isinstance(veplot, vedo.Plotter)
    veplot += mesh

    particles_to_plot = [particle_monitor[pid] for pid in pid_to_plot]
    lines = [_create_trajectory_line(particle)
             for particle in particles_to_plot]
    points = _create_all_points(
        particles_to_plot,
        add_extrapolated_position=add_extrapolated_position,
    )

    veplot += lines + points
    veplot.show()
    return veplot
