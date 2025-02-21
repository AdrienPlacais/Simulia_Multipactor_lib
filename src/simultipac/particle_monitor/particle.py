"""Define :class:`Particle`, created by reading CST ParticleMonitor files."""

import logging
import math

import numpy as np
import vedo
from numpy.typing import NDArray

from simultipac.constants import clight, qelem
from simultipac.particle_monitor.converters import (
    adim_momentum_to_eV,
    adim_momentum_to_speed_mm_per_ns,
)

PartMonLine = tuple[str, str, str, str, str, str, str, str, str, str, str, str]
PartMonData = tuple[
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    int,
    int,
]


class Particle:  # pylint: disable=too-many-instance-attributes
    """Holds evolution of position and adim momentum with time.

    Position in :unit:`mm`, time in :unit:`ns`.

    Attributes
    ----------
    _posx, _posy, _posz : list[float]
        Position in m at each time step along each direction.
    pos : np.ndarray
        Position in :unit:`mm` along the three directions stored in a single
        array.
    _momx _momy, _momz : list[float]
        Adimensional momentum at each time step along each direction.
    mom : np.ndarray
        Adimensional momentum along three directions stored in a single array.
    extrapolated_pos : np.ndarray | None
        Position in :unit:`mm`, extrapolated to refine the position of
        collision.
    extrapolated_mom : np.ndarray | None
        Adimensional momentum, extrapolated to refine the momentum of
        collision.
    _masses : list[float] | np.ndarray
        Mass of particle at each time step. An error is raised if it changes
        between two files.
    mass : float
        Mass of the particle in :unit:`kg`.
    mass_eV : float
        Mass of the particle in :unit:`eV`.
    _charges : list[float] | np.ndarray
        Charge of particle at each time step. An error is raised if it changes
        between two files.
    charge : float
        Charge of the particle.
    macro_charge : list[float] | np.ndarray
        Charge of the macro-particle.
    time : list[float] | np.ndarray
        Holds the time steps in :unit:`ns` corresponding to every value of
        ``pos``, ``mom``, etc.
    particle_id : int
        Unique id for the particle.
    source_id : {0, 1}
        Gives information on how the particle was created.
    extrapolated_times : np.ndarray | None
        Times at which position and momentum are extrapolated.

    """

    def __init__(self, raw_line: PartMonLine) -> None:
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

        self._masses: list[float]
        self.mass: float
        self.mass_eV: float  # pylint: disable=invalid-name
        self._charges: list[float]
        self.charge: float
        self._macro_charge: list[float]
        self._time: list[float]
        self.particle_id: int
        self.source_id: int

        _line = _str_to_correct_types(raw_line)
        self._posx = [_line[0]]
        self._posy = [_line[1]]
        self._posz = [_line[2]]
        self._momx = [_line[3]]
        self._momy = [_line[4]]
        self._momz = [_line[5]]
        self._masses = [_line[6]]
        self._charges = [_line[7]]
        self._macro_charge = [_line[8]]
        self._time = [_line[9]]
        self.particle_id = _line[10]
        self.source_id = _line[11]

        self.alive_at_end = False
        self.collision_cell_id: np.ndarray = np.array([], dtype=np.float64)
        self.collision_point: np.ndarray = np.array([], dtype=np.uint32)
        self.collision_angle: float = np.nan

    def add_a_file(self, raw_line: PartMonLine) -> None:
        """Add a time-step/a file to the current Particle."""
        line = _str_to_correct_types(raw_line)
        self._posx.append(line[0])
        self._posy.append(line[1])
        self._posz.append(line[2])
        self._momx.append(line[3])
        self._momy.append(line[4])
        self._momz.append(line[5])

        self._masses.append(line[6])
        self._charges.append(line[7])
        self._macro_charge.append(line[8])
        self._time.append(line[9])

    def finalize(self) -> None:
        """Post treat Particles for consistency checks, better data types."""
        self._check_constanteness_of_some_attributes()
        self._some_values_to_array()
        self._switch_to_mm_ns_units()
        if not _is_sorted(self.time):
            self._sort_by_increasing_time_values()

    def _check_constanteness_of_some_attributes(self) -> None:
        """Ensure that mass and charge did not evolve during simulation."""
        self.mass = _get_constant(self._masses)
        self.mass_eV = self.mass * clight**2 / qelem
        self.charge = _get_constant(self._charges)

    def _some_values_to_array(self) -> None:
        """Tranform position, momentum and time lists to np.arrays."""
        self.pos = np.column_stack((self._posx, self._posy, self._posz))
        self.mom = np.column_stack((self._momx, self._momy, self._momz))
        self.time = np.array(self.time)

    @property
    def macro_charge(self) -> NDArray[np.float64]:
        """Return macro charge as an array."""
        return np.array(self._macro_charge)

    def _switch_to_mm_ns_units(self) -> None:
        """Change the system units to limit rounding errors.

        .. warning::
            In CST Particle Monitor files, the time is given in seconds *
            1e-18 (aka nano-nanoseconds).  Tested with CST units for time in
            nanoseconds.

        """
        self.pos *= 1e3  # :unit:`mm`
        self.time *= 1e18  # :unit:`ns`
        # I do not know why, but time is in s * 1e-18 (aka nanonanoseconds)

    def _sort_by_increasing_time_values(self) -> None:
        """Sort arrays by increasing time values."""
        idx = np.argsort(self.time)

        self.pos = self.pos[idx]
        self.mom = self.mom[idx]
        self.macro_charge = self.macro_charge[idx]
        self.time = self.time[idx]

    @property
    def emission_energy(self) -> float:
        """Compute emission energy in eV."""
        return adim_momentum_to_eV(self.mom[0], self.mass_eV)

    def collision_energy(
        self,
        extrapolation: bool = True,
    ) -> float | None:
        """Determine the impact energy in :unit:`eV`.

        Parameters
        ----------
        extrapolation : bool, optional
            If True, perform an extrapolation of the last time steps to
            increase the precision. The default is True.

        Returns
        -------
        energy: float
            The last known energy in :unit:`eV`.

        Raises
        ------
        NotImplementedError : If extrapolation is True.

        """
        if extrapolation:
            raise NotImplementedError(
                "TODO: extrapolation of on last time  steps for better "
                "precision."
            )
        return adim_momentum_to_eV(self.mom[-1], self.mass_eV)

    def extrapolate_pos_and_mom_one_time_step_further(self) -> None:
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
        n_extrapolated_points = 2
        n_extrapolated_time_steps = 10

        self.extrapolated_times = np.full(n_extrapolated_points, np.nan)
        self.extrapolated_pos = np.full((n_extrapolated_points, 3), np.nan)
        self.extrapolated_mom = np.full((n_extrapolated_points, 3), np.nan)

        if self.time.shape[0] <= 1:
            return

        fit_end = self.time[-1]
        time_step = self.time[-1] - self.time[-2]
        extrapolated_time_end = fit_end + n_extrapolated_time_steps * time_step
        self.extrapolated_times = np.linspace(
            fit_end, extrapolated_time_end, n_extrapolated_points
        )

        self.extrapolated_pos = _extrapolate_position(
            self.pos[-1], self.mom[-1], self.extrapolated_times - fit_end
        )

        n_time_steps_for_polynom_fitting = 3
        poly_fit_deg = 2

        if poly_fit_deg >= n_time_steps_for_polynom_fitting:
            raise OSError(
                f"You need at least {poly_fit_deg + 1} momentum and "
                "time step(s) to extrapolate momentum with a degree "
                f"{poly_fit_deg} polynom."
            )

        if n_time_steps_for_polynom_fitting > self.time.shape[0]:
            return

        known_time = self.time[-n_time_steps_for_polynom_fitting:]
        known_mom = self.mom[-n_time_steps_for_polynom_fitting:, :]
        self.extrapolated_mom = _extrapolate_momentum(
            known_time, known_mom, self.extrapolated_times, poly_fit_deg
        )

    def determine_if_alive_at_end(
        self, max_time: float, tol: float = 1e-6
    ) -> None:
        """Determine if the particle collisioned before end of simulation."""
        if abs(max_time - self.time[-1]) < tol:
            self.alive_at_end = True

    def find_collision(
        self,
        mesh: vedo.Mesh,
        warn_no_collision: bool = True,
        warn_multiple_collisions: bool = True,
        **kwargs,
    ) -> None:
        """Find where the trajectory impacts the structure.

        If the particle is alive at the end of the simulation, we do not even
        try. If it has only one known time step, neither do we.

        We first try to detect a collision between the last known position of
        the particle and the last extrapolated position. If no collision is
        found, we try to find it between the last known position and the
        know position just before that.

        .. note::
            If the last extrapolated position is too far from the last known
            position, several collisions may be detected.

        .. todo::
            Take only nearest cell instead of the one with the lowest ID as for
            now.

        Parameters
        ----------
        mesh : vedo.Mesh
            ``vedo`` mesh object describing the structure of the rf system.
        warn_no_collision : bool, optional
            If True, a warning is raised when the electron was not alive at the
            end of the simulation, but no collision was detected. The default
            is True.
        warn_multiple_collisions : bool
            To warn if several collisions were detected for the same particle.
            Also remove all collisions but the first one. The default is True.
        kwargs :
            kwargs

        """
        if self.alive_at_end:
            return
        if self.pos.shape[0] <= 1:
            return

        p_0 = self.pos[-1]
        assert self.extrapolated_pos is not None
        p_1 = self.extrapolated_pos[-1]

        collision_point, collision_cell = mesh.intersect_with_line(
            p0=p_0, p1=p_1, return_ids=True, tol=0
        )

        if collision_point.shape[0] == 0:
            if self.pos.shape[0] <= 2:
                return
            p_1 = p_0
            p_0 = self.pos[-2]
            collision_point, collision_cell = mesh.intersect_with_line(
                p0=p_0, p1=p_1, return_ids=True, tol=0
            )

        if warn_no_collision and collision_point.shape[0] == 0:
            logging.info(f"No collision for particle {self.particle_id}.")
            return

        if collision_point.shape[0] > 1:
            collision_point = collision_point[0, :]
            collision_cell = collision_cell[0, np.newaxis]
            if warn_multiple_collisions:
                logging.warning(
                    "More than one collision for particle "
                    f"{self.particle_id}. Only considering the first."
                )

        self.collision_cell_id = collision_cell
        self.collision_point = collision_point
        return

    def compute_collision_angle(
        self,
        mesh: vedo.Mesh,
    ) -> None:
        """Compute the angle of impact."""
        if self.alive_at_end:
            return
        if self.collision_cell_id.shape[0] < 1:
            return

        direction = self.mom[-1]
        normal = mesh.cell_normals[self.collision_cell_id]
        adjacent = normal.dot(direction)
        opposite = np.linalg.norm(np.cross(normal, direction))
        tan_theta = opposite / adjacent
        self.collision_angle = abs(math.atan(tan_theta))


def _str_to_correct_types(line: PartMonLine) -> PartMonData:
    """Convert the input line of strings to proper data types."""
    corrected = (
        float(line[0]),
        float(line[1]),
        float(line[2]),
        float(line[3]),
        float(line[4]),
        float(line[5]),
        float(line[6]),
        float(line[7]),
        float(line[8]),
        float(line[9]),
        int(line[10]),
        int(line[11]),
    )
    return corrected


def _get_constant(variables: list[float]) -> float:
    """Check that the list of floats is a constant, return constant."""
    asarray = np.array(variables)
    if not (asarray == asarray[0]).all():
        raise ValueError
    return asarray[0]


def _is_sorted(array: np.ndarray) -> bool:
    """Check that given array is ordered (increasing values)."""
    return (array == np.sort(array)).all()


def _extrapolate_position(
    last_pos: np.ndarray, last_mom: np.ndarray, desired_time: np.ndarray
) -> np.ndarray:
    """Extrapolate the position using the last known momentum.

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


def _extrapolate_momentum(
    known_time: np.ndarray,
    known_mom: np.ndarray,
    desired_time: np.ndarray,
    poly_fit_deg: int,
) -> np.ndarray:
    """Extrapolate the momentum.

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
                desired_mom[time, axis] += (
                    polynom[deg, axis] * desired_time[time] ** deg
                )

    return desired_mom
