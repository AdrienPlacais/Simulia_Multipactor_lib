"""Define simple classes to lighten :class:`.Particle`."""

import logging
from collections.abc import Iterable, Sequence

import numpy as np
from numpy.typing import NDArray

from simultipac.particle_monitor.converters import (
    adim_momentum_to_speed_mm_per_ns,
)


class Vector:
    """Hold a vector with three coordinates."""

    def __init__(
        self,
        x: Sequence[float] | None = None,
        y: Sequence[float] | None = None,
        z: Sequence[float] | None = None,
        is_extrapolated: bool = False,
    ) -> None:
        """Create empty lists."""
        self.x: list[float] = list(x) if x is not None else []
        self.y: list[float] = list(y) if y is not None else []
        self.z: list[float] = list(z) if z is not None else []

        self._array: NDArray[np.float64] | None = None

        self._is_extrapolated = is_extrapolated
        self.extrapolated: Vector
        if not is_extrapolated:
            self.extrapolated = Vector(is_extrapolated=True)
        self._is_reordered = False
        self._is_normalized = False

    def append(self, coords: Sequence[float]) -> None:
        """Append new coordinates. Reset ``array``."""
        if self._is_normalized or self._is_reordered:
            logging.warning(
                "Normal behavior is following: load all data first, modify it "
                "(sorting, normalization) afterwards."
            )
        self.x.append(coords[0])
        self.y.append(coords[1])
        self.z.append(coords[2])
        if self._array is not None:
            self._array = None

    def reorder(self, ordered_time_idx: NDArray[np.int64]) -> None:
        """Sort coordinates by increasing time values."""
        self.x = [self.x[i] for i in ordered_time_idx]
        self.y = [self.y[i] for i in ordered_time_idx]
        self.z = [self.z[i] for i in ordered_time_idx]
        if self._array is not None:
            self._array = None

    def extrapolate(self, *args, **kwargs) -> None:
        """Extrapolate vector one time step further."""
        if self._array is not None:
            self._array = None
        self._is_extrapolated = True

    def normalize(self) -> None:
        """Normalize to proper units."""
        if self._array is not None:
            self._array = None
        self._is_normalized = True

    @property
    def array(self) -> NDArray[np.float64]:
        """2D array, of shape (N, 3) where N is number of time steps.

        .. note::
            ``array[10, 0]``: x coordinate at 11th time step
            ``array[0, 10]``: NO

        """
        if self._array is None:
            self._array = np.column_stack([self.x, self.y, self.z])
        return self._array


class Momentum(Vector):
    """Specialized class for momentum."""

    def extrapolate(
        self,
        known_times: NDArray[np.float64],
        desired_times: NDArray[np.float64],
        *,
        poly_fit_deg: int,
    ) -> None:
        """Extrapolate the momentum.

        Parameters
        ----------
        known_times : NDArray
            1D array containing x-data used for extrapolation.
        desired_times : NDArray
            1D array containing time momentum should be extrapolated on. Should
            not start at 0.
        poly_fit_deg : int
            Degree of the polynomial fit.

        """
        polynom = np.polyfit(known_times, self.array, poly_fit_deg)
        polynom = np.flip(polynom, axis=0)

        n_time_subdivisions = desired_times.shape[0]
        for i in range(n_time_subdivisions):
            new = [0.0, 0.0, 0.0]
            for deg in range(poly_fit_deg + 1):
                for j in range(3):
                    new[j] += polynom[deg, j] * desired_times[i] ** deg
            self.extrapolated.append(new)

        return super().extrapolate()


class Position(Vector):
    """Specialized class for position."""

    def extrapolate(
        self,
        momentum: NDArray[np.float64] | Momentum,
        delta_t: Iterable[float] | NDArray[np.float64],
    ) -> None:
        """Extrapolate the position using the last known momentum.

        This is a first-order approximation. We consider that the momentum is
        constant over ``desired_time``. Not adapted to extrapolation on long
        time spans.

        .. todo::
            Check is position is normalized or not.

        Parameters
        ----------
        momentum : NDArray | Momentum
            1D array containing last known momentum, adimensionned.
        delta_t : Iterable[float] | NDArray[np.float64]
            1D array containing time at which position should be extrapolated.
            Should look like ``[delta, 2*delta, 3*delta]``.

        """
        if isinstance(momentum, Momentum):
            momentum = momentum.array[-1, :]
        last_speed = adim_momentum_to_speed_mm_per_ns(momentum)
        last_pos = self.array[-1, :]

        for time in delta_t:
            new_pos = [last_pos[i] + last_speed[i] * time for i in range(3)]
            self.extrapolated.append(new_pos)
        return super().extrapolate()

    def normalize(self) -> None:
        """Change units to :unit:`mm`."""
        self.x = [x * 1e3 for x in self.x]
        self.y = [y * 1e3 for y in self.y]
        self.z = [z * 1e3 for z in self.z]
        return super().normalize()
