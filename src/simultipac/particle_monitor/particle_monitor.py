"""Define :class:`ParticleMonitor`.

This dictionary-based  object holds :class:`Particle` objects. Keys of the
dictionary are the particle id of the :class:`Particle`.

.. todo::
    Raise error when folder is not found.

"""

import os
from collections.abc import Generator
from pathlib import Path
from typing import overload

import numpy as np
import vedo

from simultipac.loaders.loader_cst import particle_monitor
from simultipac.particle_monitor.particle import Particle


class ParticleMonitor(dict):
    """
    Holds all :class:`Particle` objects as values, particle id as keys.

    Attributes
    ----------
    max_time : float
        Time at which the simulation ended.

    """

    def __init__(self, folder: Path, delimiter: str | None = None) -> None:
        """Create the object, ordered list of filepaths beeing provided.

        Parameters
        ----------
        folder : Path
            Folder where all the CST ParticleMonitor files are stored.
        delimiter : str | None, optional
            Delimiter used to separate columns in the CST ParticleMonitor
            files. The default is None.

        """
        dict_of_parts: dict[int, Particle] = {}

        filepaths = list(_absolute_file_paths(folder))

        for filepath in filepaths:
            particles_info = particle_monitor(filepath, delimiter=delimiter)

            for particle_info in particles_info:
                # what is this??
                particle_id = int(particle_info[10])
                if particle_id in dict_of_parts:
                    dict_of_parts[particle_id].add_a_file(*particle_info)
                    continue
                dict_of_parts[particle_id] = Particle(*particle_info)

        for particle in dict_of_parts.values():
            particle.finalize()
            particle.extrapolate_pos_and_mom_one_time_step_further()

        super().__init__(dict_of_parts)

        self.max_time = max([part.time[-1] for part in self.values()])
        for particle in self.values():
            particle.determine_if_alive_at_end(self.max_time)

    @property
    def seed_electrons(self) -> dict[int, Particle]:
        """Return only seed electrons."""
        return _filter_source_id(self, 0)

    @property
    def emitted_electrons(self) -> dict[int, Particle]:
        """Return only emitted electrons."""
        return _filter_source_id(self, 1)

    def __str__(self) -> str:
        """Resume information on the simulation."""
        n_total_particles = len(self.keys())
        n_seed_electrons = len(self.seed_electrons.keys())
        n_emitted_electrons = len(self.emitted_electrons.keys())
        n_collisions = len(_filter_out_alive_at_end(self).keys())
        n_alive_at_end = len(_filter_out_dead_at_end(self).keys())
        out = f"This simulation involved {n_total_particles} electrons."
        out += f"\n\t{n_seed_electrons} where seed electrons."
        out += f"\n\t{n_emitted_electrons} where emitted electrons."
        out += f"\n\t{n_alive_at_end} where still alive at end of simulation."
        out += f"\n\tThere was {n_collisions} collisions."
        return out

    def emission_energies(
        self, source_id: int | None = None, to_numpy: bool = True
    ) -> list[float]:
        """Get emission energies of all or only a subset of particles."""
        subset = self
        if source_id is not None:
            subset = _filter_source_id(subset, source_id)
        out = [part.emission_energy for part in subset.values()]
        if to_numpy:
            return np.array(out)
        return out

    def collision_energies(
        self,
        source_id: int | None = None,
        to_numpy: bool = True,
        extrapolation: bool = True,
        remove_alive_at_end: bool = True,
    ) -> None:
        """
        Get all collision energies in eV.

        Parameters
        ----------
        source_id : int | None, optional
            If set, we only take particles which source_id is ``source_id``.
            The default is None.
        to_numpy : bool, optional
            If True, output list is transformed to an array. The default is
            True.
        extrapolation : bool, optional
            If True, we extrapolate over the last time steps to refine the
            collision energy. Otherwise, we simply take the last known energy
            of the particle. The default is True.
        remove_alive_at_end : bool, optional
            To remove particles alive at the end of the simulation (did not
            impact a wall). The default is True.

        """
        subset = self
        if source_id is not None:
            subset = _filter_source_id(subset, source_id)
        if remove_alive_at_end:
            subset = _filter_out_alive_at_end(subset)

        out = [
            part.collision_energy(extrapolation) for part in subset.values()
        ]
        if to_numpy:
            return np.array(out)
        return out

    @overload
    def last_known_position(
        self,
        source_id: int | None = None,
        to_numpy: bool = True,
        remove_alive_at_end: bool = True,
    ) -> np.ndarray[np.float64]: ...

    @overload
    def last_known_position(
        self,
        source_id: int | None = None,
        to_numpy: bool = True,
        remove_alive_at_end: bool = False,
    ) -> list[np.ndarray[np.float64]]: ...

    def last_known_position(
        self,
        source_id: int | None = None,
        to_numpy: bool = True,
        remove_alive_at_end: bool = True,
    ) -> list[np.ndarray[np.float64]] | np.ndarray[np.float64]:
        """
        Get the last recorded position of every particle.

        Parameters
        ----------
        source_id : int | None, optional
            If set, we only take particles which source_id is ``source_id``.
            The default is None.
        to_numpy : bool, optional
            If True, output list is transformed to an array. The default is
            True.
        remove_alive_at_end : bool, optional
            To remove particles alive at the end of the simulation (did not
            impact a wall). The default is True.

        Returns
        -------
        out : list[np.ndarray[np.float64]] | np.ndarray[np.float64]
            Last known position in :unit:`mm` of every particle.

        """
        subset = self
        if source_id is not None:
            subset = _filter_source_id(subset, source_id)
        if remove_alive_at_end:
            subset = _filter_out_alive_at_end(subset)

        out = [part.pos[-1] for part in subset.values()]
        if to_numpy:
            return np.array(out)
        return out

    @overload
    def last_known_direction(
        self,
        source_id: int | None = None,
        to_numpy: bool = True,
        normalize: bool = True,
        remove_alive_at_end: bool = True,
    ) -> np.ndarray[np.float64]: ...

    @overload
    def last_known_direction(
        self,
        source_id: int | None = None,
        to_numpy: bool = False,
        normalize: bool = True,
        remove_alive_at_end: bool = True,
    ) -> list[np.ndarray[np.float64]]: ...

    def last_known_direction(
        self,
        source_id: int | None = None,
        to_numpy: bool = True,
        normalize: bool = True,
        remove_alive_at_end: bool = True,
    ) -> list[np.ndarray[np.float64]] | np.ndarray[np.float64]:
        """
        Get the last recorded direction of every particle.

        .. todo::
            Why did I choose to compute position difference rather than just
            taking the momentum array when not normalizing???

        Parameters
        ----------
        source_id : int | None, optional
            If set, we only take particles which source_id is ``source_id``.
            The default is None.
        to_numpy : bool, optional
            If True, output list is transformed to an array. The default is
            True.
        normalize : bool, optional
            To normalize the direction vector. The default is True.
        remove_alive_at_end : bool, optional
            To remove particles alive at the end of the simulation (did not
            impact a wall). The default is True.

        Returns
        -------
        out : list[np.ndarray[np.float64]] | np.ndarray[np.float64]
            Last known moment vector of every particle.

        """
        subset = self
        if source_id is not None:
            subset = _filter_source_id(subset, source_id)
        if remove_alive_at_end:
            subset = _filter_out_alive_at_end(subset)

        out = [part.mom[-1] for part in subset.values()]

        if normalize:
            out = [mom / np.linalg.norm(mom) for mom in out]

        if to_numpy:
            return np.array(out)
        return out

    def compute_collision_angles(self, mesh: vedo.Mesh, **kwargs) -> None:
        """Find all collisions."""
        mesh.compute_normals(points=False, cells=True)
        for particle in self.values():
            particle.find_collision(mesh, **kwargs)
            particle.compute_collision_angle(mesh)


def _absolute_file_paths(directory: Path) -> Generator[Path, Path, None]:
    """Get all filepaths in absolute from dir, remove unwanted files."""
    for dirpath, _, filenames in os.walk(directory):
        for dirpath, _, filenames in os.walk(directory):
            for f in filenames:
                f = Path(f)
                if f.suffix in (".swp",):
                    continue
                yield Path(dirpath, f)


def _filter_source_id(
    input_dict: dict[int, Particle],
    wanted_id: int,
) -> dict[int, Particle]:
    """Filter Particles against the sourceID field."""
    return {
        pid: part
        for pid, part in input_dict.items()
        if part.source_id == wanted_id
    }


def _filter_out_dead_at_end(
    input_dict: dict[int, Particle]
) -> dict[int, Particle]:
    """Filter out Particles that collisioned during simulation."""
    particles_alive_at_end = {
        pid: part for pid, part in input_dict.items() if part.alive_at_end
    }
    return particles_alive_at_end


def _filter_out_alive_at_end(
    input_dict: dict[int, Particle],
) -> dict[int, Particle]:
    """Filter out Particles that were alive at the end of simulation."""
    particles_that_collisioned_during_simulation = {
        pid: part for pid, part in input_dict.items() if not part.alive_at_end
    }
    return particles_that_collisioned_during_simulation


def _filter_out_part_with_one_time_step(
    input_dict: dict[int, Particle]
) -> dict[int, Particle]:
    """Remove particle with only one known position.

    This is useful when the time resolution is low.

    """
    return {
        pid: part for pid, part in input_dict.items() if len(part.time) > 1
    }
