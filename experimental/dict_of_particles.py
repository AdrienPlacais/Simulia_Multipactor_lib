#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 12:36:42 2023.

@author: placais
"""
import os

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


def _absolute_file_paths(directory: str) -> list[str]:
    """Get all filepaths in absolute from dir, remove unwanted files."""
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            if os.path.splitext(f)[1] in ['.swp']:
                continue
            yield os.path.abspath(os.path.join(dirpath, f))
