"""Define the functions to convert momentum and speeds."""

import numpy as np
from numpy._typing import NDArray

from simultipac.constants import clight, clight_in_mm_per_ns


def adim_momentum_to_speed_m_per_s(
    mom: NDArray[np.float64],
) -> NDArray[np.float64]:
    """Convert adim momentum to speed in :unit:`m/s`.

    From the Position Monitor files header:

    .. note::
        Momentum is normalized to the product of particle's mass and speed of
        light.

    So ``mom`` is adimensional: normalisation = mass * clight
    And we de-normalize with:
    momentum_in_kg_m_per_s = ``mom`` * normalisation
    speed_in_m_per_s = momentum_in_kg_m_per_s / mass = ``mom`` * clight

    Parameters
    ----------
    mom : numpy.ndarray
        A 1D or 2D array holding adimensionned momentum along the three
        directions of one or several particles.

    Returns
    -------
    speed_in_m_per_s : numpy.ndarray
        A 2D array holding the speed along the three directions of one or
        several particles.

    """
    if len(mom.shape) == 1:
        mom = np.expand_dims(mom, 0)
    speed_in_m_per_s = mom * clight
    return speed_in_m_per_s


def adim_momentum_to_speed_mm_per_ns(
    mom: NDArray[np.float64],
) -> NDArray[np.float64]:
    """Convert adimensionned momentum to speed in :unit:`mm/ns`.

    Parameters
    ----------
    mom : numpy.ndarray
        A 1D or 2D array holding adimensionned momentum along the three
        directions of one or several particles.

    Returns
    -------
    speed_in_mm_per_ns : numpy.ndarray
        A 2D array holding the speed along the three directions of one or
        several particles.

    """
    if len(mom.shape) == 1:
        mom = np.expand_dims(mom, 0)
    speed_in_mm_per_ns = mom * clight_in_mm_per_ns
    return speed_in_mm_per_ns


def adim_momentum_to_eV(mom: NDArray[np.float64], mass_eV: float) -> float:
    """Convert adimensionned momentum to energy in :unit:`eV`.

    Parameters
    ----------
    mom : numpy.ndarray
        A 1D or 2D array holding adimensionned momentum along the three
        directions of one particle.

    Returns
    -------
    energy : float
        The energy of the particle in :unit:`eV`.

    """
    energy = 0.5 * float(np.linalg.norm(mom)) ** 2 * mass_eV
    return energy
