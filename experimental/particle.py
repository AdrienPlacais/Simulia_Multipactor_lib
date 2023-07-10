#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 12:35:01 2023.

@author: placais
"""
import numpy as np

from multipactor.experimental.particle_monitors_converters import (
    momentum_to_eV
)


class Particle:
    """Holds mass, charge, evolution of position."""

    def __init__(self, *line: str) -> None:
        """Init from a line of a position_monitor file."""
        self._posx: list[float]
        self._posy: list[float]
        self._posz: list[float]
        self.pos: np.ndarray
        self._momx: list[float]
        self._momy: list[float]
        self._momz: list[float]
        self.mom: np.ndarray

        self._masses: list[float] | np.ndarray
        self.mass: float
        self._charges: list[float] | np.ndarray
        self.charge: float
        self.macro_charge: list[float] | np.ndarray
        self.time: list[float] | np.ndarray
        self.particle_id: int
        self.source_id: int

        line = _str_to_correct_types(line)
        self._posx = [line[0]]
        self._posy = [line[1]]
        self._posz = [line[2]]
        self._momx = [line[3]]
        self._momy = [line[4]]
        self._momz = [line[5]]
        self._masses = [line[6]]
        self._charges = [line[7]]
        self.macro_charge = [line[8]]
        self.time = [line[9]]
        self.particle_id = line[10]
        self.source_id = line[11]

    def add_a_file(self, *line: str) -> None:
        """Add a time-step/a file to the current Particle."""
        line = _str_to_correct_types(line)
        self._posx.append(line[0])
        self._posy.append(line[1])
        self._posz.append(line[2])
        self._momx.append(line[3])
        self._momy.append(line[4])
        self._momz.append(line[5])

        self._masses.append(line[6])
        self._charges.append(line[7])
        self.macro_charge.append(line[8])
        self.time.append(line[9])

    def finalize(self) -> None:
        """Post treat Particles for consistency checks, better data types."""
        self._check_constanteness_of_some_attributes()
        self._some_values_to_array()
        if not _is_sorted(self.time):
            self._sort_by_increasing_time_values()

    def _check_constanteness_of_some_attributes(self) -> None:
        """Ensure that mass and charge did not evolve during simulation."""
        isconstant, constant = _get_constant(self._masses)
        if not isconstant:
            raise IOError("Variation of mass during simulation.")
        self.mass = constant

        isconstant, constant = _get_constant(self._charges)
        if not isconstant:
            raise IOError("Variation of charge during simulation.")
        self.charge = constant

    def _some_values_to_array(self) -> None:
        """Tranform position, momentum and time lists to np.arrays."""
        self.pos = np.column_stack((self._posx, self._posy, self._posz))
        self.mom = np.column_stack((self._momx, self._momy, self._momz))
        self.macro_charge = np.array(self.macro_charge)
        self.time = np.array(self.time)

    def _sort_by_increasing_time_values(self) -> None:
        """Sort arrays by increasing time values."""
        idx = np.argsort(self.time)

        self.pos = self.pos[idx]
        self.mom = self.mom[idx]
        self.macro_charge = self.macro_charge[idx]
        self.time = self.time[idx]

    def detect_collision(self) -> None:
        """Determine when and where the collision took place."""
        pass

    def get_collision_energy(self) -> float:
        """Determine the impact energy."""
        pass

    def get_collision_angle(self) -> float:
        """Determine the impact incidence angle, w.r.t. the surface normal."""
        pass

    @property
    def emission_energy(self) -> float:
        """Compute emission energy in eV."""
        return momentum_to_eV(self.mom[0], self.mass, self.charge)


def _str_to_correct_types(line: tuple[str]) -> tuple[float | int]:
    """Convert the input line of strings to proper data types."""
    corrected = (float(line[0]), float(line[1]), float(line[2]),
                 float(line[3]), float(line[4]), float(line[5]),
                 float(line[6]),
                 float(line[7]),
                 float(line[8]),
                 float(line[9]),
                 int(line[10]),
                 int(line[11])
                 )
    return corrected


def _get_constant(variables: list[float]) -> tuple[bool, float | None]:
    """Check that the list of floats is a constant, return constant."""
    asarray = np.array(variables)
    if not (asarray == asarray[0]).all():
        return False, None

    return True, asarray[0]


def _is_sorted(array: np.ndarray) -> bool:
    """Check that given array is ordered (increasing values)."""
    return (array == np.sort(array)).all()
