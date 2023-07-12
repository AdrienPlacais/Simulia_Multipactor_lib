#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 15:04:56 2023.

@author: placais
"""
import numpy as np

from multipactor.constants import clight, qelec


def adim_momentum_to_speed_m_per_s(mom: np.ndarray, mass: float) -> np.ndarray:
    """
    Convert adim momentum to speed in m/s.

    From the Position Monitor files header:
        Momentum is normalized to the product of particle's mass and speed of
        light.

    So `mom` is adimensional:
        normalisation = mass * clight
    And we de-normalize with:
        momentum_in_kg_m_per_s = `mom` * normalisation
        speed_in_m_per_s = momentum_in_kg_m_per_s / mass
                         = `mom` * clight

    """
    if len(mom.shape) == 1:
        mom = np.expand_dims(mom, 0)
    speed_in_m_per_s = mom * clight
    return speed_in_m_per_s


def adim_momentum_to_speed_mm_per_ns(mom: np.ndarray, mass: float
                                     ) -> np.ndarray:
    """Convert adim momentum to speed in mm/ns."""
    speed_in_m_per_s = adim_momentum_to_speed_m_per_s(mom, mass)
    return speed_in_m_per_s * 1e-6


def adim_momentum_to_eV(mom: np.ndarray, mass: float) -> np.ndarray:
    """Convert adim momentum to energy in eV."""
    if len(mom.shape) == 1:
        mom = np.expand_dims(mom, 0)
    speed_in_m_per_s = adim_momentum_to_speed_m_per_s(mom, mass)
    energy_in_J = 0.5 * mass * np.linalg.norm(speed_in_m_per_s)**2
    energy_in_eV = energy_in_J / qelec
    return energy_in_eV
