#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 15:04:56 2023.

@author: placais
"""
import numpy as np

from multipactor.constants import clight


def momentum_to_eV(mom: np.ndarray, mass: float, charge: float) -> float:
    """
    Convert momentum to energy in eV.

    From the Position Monitor files header:
        Momentum is normalized to the product of particle's mass and speed of
        light.

    So:
        normalisation = mass * clight
    And we de-normalize with:
        momentum_in_kg_per_s = `mom` * normalisation

    Orders of magnitude are very wrong. So I think we should understand:
        Momentum is multiplied by the speed of light.

    """
    momentum_in_kg_m_per_s = mom / clight
    speed_in_m_per_s = momentum_in_kg_m_per_s / mass
    energy_in_J = np.sqrt(speed_in_m_per_s[0]**2
                          + speed_in_m_per_s[1]**2
                          + speed_in_m_per_s[2]**2)
    energy_in_eV = np.abs(charge) * energy_in_J
    return energy_in_eV
