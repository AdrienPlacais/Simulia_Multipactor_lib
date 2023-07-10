#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 15:55:49 2023.

@author: placais
"""
import numpy as np

from multipactor.experimental.dict_of_particles import DictOfParticles
from multipactor.visualization.plot import create_fig_if_not_exists


def plot_emission_energies(particles: DictOfParticles) -> None:
    fig, axx = create_fig_if_not_exists(2, sharex=True, num=2)
    axx[1].set_xlabel("Emission energy [eV]")
    axx[0].set_ylabel("Seed electrons")
    axx[1].set_ylabel("Emitted electrons")

    for i in range(2):
        emission_energies = particles.emission_energies(source_id=i,
                                                        to_numpy=True)
        counts, bins = np.histogram(emission_energies)
        axx[i].hist(bins[:-1], bins, weights=counts)
        axx[i].grid(True)
