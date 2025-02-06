"""Define the functions to convert momentum and speeds."""

import numpy as np

from simultipac.constants import clight, clight_in_mm_per_ns


def adim_momentum_to_speed_m_per_s(mom: np.ndarray) -> np.ndarray:
    """Convert adim momentum to speed in :unit:`m/s`.

    From the Position Monitor files header:

    .. note::
        Momentum is normalized to the product of particle's mass and speed of
        light.

    So ``mom`` is adimensional: normalisation = mass * clight
    And we de-normalize with:
    momentum_in_kg_m_per_s = ``mom`` * normalisation
    speed_in_m_per_s = momentum_in_kg_m_per_s / mass = ``mom`` * clight

    """
    if len(mom.shape) == 1:
        mom = np.expand_dims(mom, 0)
    speed_in_m_per_s = mom * clight
    return speed_in_m_per_s


def adim_momentum_to_speed_mm_per_ns(mom: np.ndarray) -> np.ndarray:
    """Convert adim momentum to speed in :unit:`mm/ns`."""
    if len(mom.shape) == 1:
        mom = np.expand_dims(mom, 0)
    speed_in_mm_per_ns = mom * clight_in_mm_per_ns
    return speed_in_mm_per_ns


def adim_momentum_to_eV(mom: np.ndarray, mass_eV: float) -> np.ndarray:
    """Convert adim momentum to energy in :unit:`eV`."""
    if len(mom.shape) == 1:
        mom = np.expand_dims(mom, 0)
    return 0.5 * np.linalg.norm(mom) ** 2 * mass_eV
