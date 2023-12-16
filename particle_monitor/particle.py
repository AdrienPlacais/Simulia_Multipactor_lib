#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 12:35:01 2023.

@author: placais

In this module we define :class:`Particle`. This object is created by
sequentially reading CST ParticleMonitor files.

"""
import numpy as np

from multipactor.constants import clight, qelem
from multipactor.particle_monitor.converters import (
    adim_momentum_to_eV, adim_momentum_to_speed_mm_per_ns
)


class Particle:  # pylint: disable=too-many-instance-attributes
    """Holds evolution of position (in mm) and adim momentum with time (ns).

    Attributes
    ----------
    _posx, _posy, _posz : list[float]
        Position in m at each time step along each direction.
    pos : np.ndarray
        Position in mm along the three directions stored in a single array.
    _momx _momy, _momz : list[float]
        Adimensional momentum at each time step along each direction.
    mom : np.ndarray
        Adimensional momentum along three directions stored in a single array.
    extrapolated_pos : np.ndarray | None
        Position in mm, extrapolated to refine the position of collision.
    extrapolated_mom : np.ndarray | None
        Adimensional momentum, extrapolated to refine the momentum of
        collision.
    _masses : list[float] | np.ndarray
        Mass of particle at each time step. An error is raised if it changes
        between two files.
    mass : float
        Mass of the particle in kg.
    mass_eV : float
        Mass of the particle in eV.
    _charges : list[float] | np.ndarray
        Charge of particle at each time step. An error is raised if it changes
        between two files.
    charge : float
        Charge of the particle.
    macro_charge : list[float] | np.ndarray
        Charge of the macro-particle.
    time : list[float] | np.ndarray
        Holds the time steps in ns corresponding to every value of ``pos``,
        ``mom``, etc.
    particle_id : int
        Unique id for the particle.
    source_id : {0, 1}
        Gives information on how the particle was created.
    extrapolated_times : np.ndarray | None
        Times at which position and momentum are extrapolated.

    """

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

        self.extrapolated_pos: np.ndarray | None = None
        self.extrapolated_mom: np.ndarray | None = None
        self.extrapolated_times: np.ndarray | None = None

        self._masses: list[float] | np.ndarray
        self.mass: float
        self.mass_eV: float  # pylint: disable=invalid-name
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
        self.alive_at_end = False

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
        self._switch_to_mm_ns_units()
        if not _is_sorted(self.time):
            self._sort_by_increasing_time_values()

    def _check_constanteness_of_some_attributes(self) -> None:
        """Ensure that mass and charge did not evolve during simulation."""
        isconstant, constant = _get_constant(self._masses)
        if not isconstant:
            raise IOError("Variation of mass during simulation.")
        self.mass = constant
        self.mass_eV = constant * clight**2 / qelem

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

    def _switch_to_mm_ns_units(self) -> None:
        """
        Change the system units to limit rounding errors.

        .. warning::
            In CST Particle Monitor files, the time is given in seconds *
            1e-18 (aka nano-nanoseconds).  Tested with CST units for time in
            nanoseconds.

        """
        self.pos *= 1e3     # mm
        self.time *= 1e18   # ns
        # I do not know why, but time is in s * 1e-18 (aka nanonanoseconds)

    def _sort_by_increasing_time_values(self) -> None:
        """Sort arrays by increasing time values."""
        idx = np.argsort(self.time)

        self.pos = self.pos[idx]
        self.mom = self.mom[idx]
        self.macro_charge = self.macro_charge[idx]
        self.time = self.time[idx]

    def detect_collision(self) -> None:
        """Determine when and where the collision took place."""
        self._extrapolate_pos_and_mom_one_time_step_further()

    def get_collision_angle(self) -> float:
        """Determine the impact incidence angle, w.r.t. the surface normal."""
        raise NotImplementedError

    @property
    def emission_energy(self) -> float:
        """Compute emission energy in eV."""
        return adim_momentum_to_eV(self.mom[0], self.mass_eV)

    def collision_energy(self, extrapolation: bool = True,
                         ) -> float | None:
        """
        Determine the impact energy in eV.

        Parameters
        ----------
        extrapolation : bool, optional
            If True, perform an extrapolation of the last time steps to
            increase the precision. The default is True.

        Returns
        -------
        energy: float
            The last known energy in eV.

        Raises
        ------
        NotImplementedError : If extrapolation is True.

        """
        if extrapolation:
            raise NotImplementedError("TODO: extrapolation of on last time "
                                      " steps for better precision.")
        return adim_momentum_to_eV(self.mom[-1], self.mass_eV)

    def _extrapolate_pos_and_mom_one_time_step_further(self) -> None:
        """
        Extrapolate position and momentum by one time-step.

        CST PIC solves the motion with a leapfrog solver (source: Mohamad
        Houssini from Keonys, private communication).
        Several possibilities:
        - ``pos`` corresponds to ``time`` and ``mom`` shifted by half
        time-steps (most probable).
        - ``mom`` corresponds to ``time`` and ``pos`` shifted by half
        time-steps (also possible).
        - ``pos`` or ``mom`` is interpolated so that both are expressed at
        full ``time`` steps (what I will consider for now).

        """
        n_extrapolated_points = 10
        self.extrapolated_times = np.full(n_extrapolated_points, np.NaN)
        self.extrapolated_pos = np.full((n_extrapolated_points, 3), np.NaN)
        self.extrapolated_mom = np.full((n_extrapolated_points, 3), np.NaN)

        if self.time.shape[0] <= 1:
            return

        fit_end = self.time[-1]
        time_step = self.time[-1] - self.time[-2]
        self.extrapolated_times = np.linspace(fit_end, fit_end + time_step,
                                              n_extrapolated_points)

        self.extrapolated_pos = _extrapolate_position(
            self.pos[-1], self.mom[-1], self.extrapolated_times - fit_end)

        n_time_steps_for_polynom_fitting = 3
        poly_fit_deg = 2

        if poly_fit_deg >= n_time_steps_for_polynom_fitting:
            raise IOError(f"You need at least {poly_fit_deg + 1} momentum and "
                          "time step(s) to extrapolate momentum with a degree "
                          f"{poly_fit_deg} polynom.")

        if n_time_steps_for_polynom_fitting > self.time.shape[0]:
            return

        known_time = self.time[-n_time_steps_for_polynom_fitting:]
        known_mom = self.mom[-n_time_steps_for_polynom_fitting:, :]
        self.extrapolated_mom = _extrapolate_momentum(known_time,
                                                      known_mom,
                                                      self.extrapolated_times,
                                                      poly_fit_deg)

    def determine_if_alive_at_end(self,
                                  max_time: float,
                                  tol: float = 1e-6) -> None:
        """Determine if the particle collisioned before end of simulation."""
        if abs(max_time - self.time[-1]) < tol:
            self.alive_at_end = True

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


def _extrapolate_position(last_pos: np.ndarray, last_mom: np.ndarray,
                          desired_time: np.ndarray) -> np.ndarray:
    """
    Extrapolate the position using the last known momentum.

    This is a first-order approximation. We consider that the momentum is
    constant over `desired_time`. Not adapted to extrapolation on long time
    spans.

    Parameters
    ----------
    last_pos : np.ndarray
        Last known position.
    last_mom : np.ndarray
        Last known momentum.
    desired_time : np.ndarray
        Time on which position should be extrapolated. Should not be too long.

    Returns
    -------
    desired_pos : np.ndarray
        Extrapolated position starting from `last_pos`, over `desired_time`
        with the constant momentum `last_mom`.

    """
    n_time_subdivisions = desired_time.shape[0]
    desired_pos = np.full((n_time_subdivisions, 3), last_pos)
    last_speed = adim_momentum_to_speed_mm_per_ns(last_mom)[0]

    for time in range(n_time_subdivisions):
        desired_pos[time, :] += last_speed * desired_time[time]
    return desired_pos


def _extrapolate_momentum(known_time: np.ndarray, known_mom: np.ndarray,
                          desired_time: np.ndarray, poly_fit_deg: int
                          ) -> np.ndarray:
    """
    Extrapolate the momentum.

    Parameters
    ----------
    known_time : np.ndarray
        x-data used for extrapolation.
    known_mom : np.ndarray
        y_data used for extrapolation.
    desired_time : np.ndarray
        Time momentum should be extrapolated on.
    poly_fit_deg : int
        Degree of the polynomial fit.

    Returns
    -------
    desired_mom : np.ndarray
        Momentum extrapolated on desired_time.

    """
    n_time_subdivisions = desired_time.shape[0]
    desired_mom = np.zeros((n_time_subdivisions, 3))

    polynom = np.polyfit(known_time, known_mom, poly_fit_deg)
    polynom = np.flip(polynom, axis=0)

    for time in range(n_time_subdivisions):
        for axis in range(3):
            for deg in range(poly_fit_deg + 1):
                desired_mom[time, axis] += polynom[deg, axis] \
                    * desired_time[time]**deg

    return desired_mom
