#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 12:36:42 2023.

@author: placais
"""
import os
import numpy as np

from multipactor.experimental.particle import Particle
from multipactor.loaders.loader_cst import particle_monitor


class DictOfParticles(dict):
    """Holds all Particles, keys of dict are Particle IDs."""

    def __init__(self, folder: str) -> None:
        """Create the object, ordered list of filepaths beeing provided."""
        dict_of_parts: dict(int, Particle) = {}

        filepaths = _absolute_file_paths(folder)

        for filepath in filepaths:
            particles_info = particle_monitor(filepath)

            for particle_info in particles_info:
                particle_id = int(particle_info[10])
                if particle_id in dict_of_parts:
                    dict_of_parts[particle_id].add_a_file(*particle_info)
                    continue
                dict_of_parts[particle_id] = Particle(*particle_info)

        for particle in dict_of_parts.values():
            particle.finalize()

        super().__init__(dict_of_parts)

        self.max_time = np.max([part.time[-1] for part in self.values()])

    @property
    def seed_electrons(self) -> dict[int, Particle]:
        """Return only seed electrons."""
        return _filter_source_id(self, 0)

    @property
    def emitted_electrons(self) -> dict[int, Particle]:
        """Return only seed electrons."""
        return _filter_source_id(self, 1)

    def emission_energies(self, source_id: int | None = None,
                          to_numpy: bool = True) -> list[float]:
        """Get emission energies of all or only a subset of particles."""
        subset = self
        if source_id is not None:
            subset = _filter_source_id(subset, source_id)
        out = [part.emission_energy for part in subset.values()]
        if to_numpy:
            return np.array(out)
        return out

    def collision_energies(self, source_id: int | None = None,
                           to_numpy: bool = True, extrapolation: bool = True,
                           remove_alive_at_end: bool = True) -> None:
        """
        Get all collision energies in eV.

        Parameters
        ----------
        source_id : int | None, optional
            If set, we only take particles which source_id is `source_id`. The
            default is None.
        to_numpy : bool, optional
            If True, output list is transformed to an array. The default is
            True.
        extrapolation : bool, optional
            If True, we extrapolate over the last time steps to refine the
            collision energy. Otherwise, we simply take the last known energy
            of the particle. The default is True.
        remove_alive_at_end : bool, optional
            If True, we do not return the particles that were alived at the end
            of the simulation, which did not make a collision. The default is
            True.

        """
        subset = self
        if source_id is not None:
            subset = _filter_source_id(subset, source_id)
        if remove_alive_at_end:
            subset = _filter_out_alive_at_end(subset, self.max_time)

        out = [part.collision_energy(extrapolation)
               for part in subset.values()]
        if to_numpy:
            return np.array(out)
        return out


def _absolute_file_paths(directory: str) -> list[str]:
    """Get all filepaths in absolute from dir, remove unwanted files."""
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            if os.path.splitext(f)[1] in ['.swp']:
                continue
            yield os.path.abspath(os.path.join(dirpath, f))


def _filter_source_id(input_dict: dict[int, Particle], wanted_id
                      ) -> dict[int, Particle]:
    """Filter Particles against the sourceID field."""
    return {pid: part for pid, part in input_dict.items()
            if part.source_id == wanted_id}


def _filter_out_alive_at_end(input_dict: dict[int, Particle], max_time: float
                             ) -> dict[int, Particle]:
    """Filter out Particles that were alive at the end of simulation."""
    return {pid: part for pid, part in input_dict.items()
            if part.time[-1] < max_time}
