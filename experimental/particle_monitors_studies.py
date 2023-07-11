#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 15:55:49 2023.

@author: placais
"""
from typing import Any
import numpy as np

from multipactor.experimental.dict_of_particles import DictOfParticles
from multipactor.visualization.plot import create_fig_if_not_exists


def plot_emission_energies(particles: DictOfParticles) -> None:
    """Plot the emission energies sorted by source id."""
    fig, axx = create_fig_if_not_exists(2, sharex=True, num=2)
    axx[1].set_xlabel("Emission energy [eV]")
    axx[0].set_ylabel("Seed electrons")
    axx[1].set_ylabel("Emitted electrons")

    for i in range(2):
        emission_energies = particles.emission_energies(source_id=i,
                                                        to_numpy=True)
        counts, bins = np.histogram(emission_energies)
        axx[i].hist(bins[:-1], bins, weights=counts)
        axx[i].grid(True)


def plot_collision_energies(particles: DictOfParticles) -> None:
    """Plot all the collision energies."""
    fig, axx = create_fig_if_not_exists(1, sharex=True, num=1)
    axx[0].set_xlabel("Collision energy [eV]")
    axx[0].set_ylabel("All electrons")

    collision_energies = particles.collision_energies(
        to_numpy=True, extrapolation=False, remove_alive_at_end=True)
    counts, bins = np.histogram(collision_energies)
    axx[0].hist(bins[:-1], bins, weights=counts)
    axx[0].grid(True)


def plot_trajectories(particles: DictOfParticles, particle_id: list[int],
                      structure: Any = None) -> None:
    """Plot some of the trajectories."""
    fig, axx = create_fig_if_not_exists(range(221, 224), num=3)

    if structure is not None:
        raise NotImplementedError("Plot of structure not implemented yet.")

    particles_to_plot = {pid: part for pid, part in particles.items()
                         if pid in particle_id}

    projections = {
        'xy': lambda pos: pos[:, :2],
        'yz': lambda pos: pos[:, 1:],
        'xz': lambda pos: pos[:, [0, 2]],
    }
    for i, (projection_name, projection) in enumerate(projections.items()):
        axx[i].set_xlabel(projection_name[0])
        axx[i].set_ylabel(projection_name[1])
        axx[i].set_aspect('equal', adjustable='box')

        for part in particles_to_plot.values():
            projected_pos = projection(part.pos)
            line, = axx[i].plot(projected_pos[:, 0], projected_pos[:, 1],
                                marker='o')

            if part.extrapolated_pos is not None:
                projected_pos = projection(part.extrapolated_pos)
                axx[i].plot(projected_pos[:, 0], projected_pos[:, 1], ls='--',
                            c=line.get_color())
