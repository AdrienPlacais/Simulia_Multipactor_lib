#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  9 10:25:07 2023.

@author: placais

In this module we define functions to load data from SPARK3D.

"""
from pathlib import Path

import numpy as np


def get_population_evolution(filepath: Path,
                             e_acc: list[float],
                             delimiter: str = ' ',
                             ) -> tuple[dict, np.ndarray]:
    """
    Get population evolution data from a SPARK3D manual export.

    Right-click on ``Multipactor results``, ``Export to CSV``.

    Parameters
    ----------
    filepath : Path
        Path to the file to be loaded.
    e_acc : list[float]
        List of accelerating field values in MV/m.
    delimiter : str, optional
        Delimiter between columns. The default is a space.

    Returns
    -------
    data : dict
        Holds evolution of electron population with time in ns.
    parameters : np.ndarray
        Array of accelerating fields in V/m.

    """
    raw_data = np.loadtxt(filepath, delimiter=delimiter)

    parameters = np.array(e_acc) * 1e6
    n_param = len(e_acc)

    # Create a list of arrays
    data = [np.column_stack((raw_data[:, 0] * 1e9, raw_data[:, i]))
            for i in range(1, n_param + 1)]
    data = {}

    # For consistency with CST import, we remove the end of MP simulations
    # (population = 0)
    for i in range(n_param):
        dat = data[i]
        idx = np.argwhere(dat[:, 1] == 0.)
        if idx.size > 0:
            data[i] = dat[:idx[0][0], :]

        data[i + 1] = {'E_acc in MV per m': e_acc[i],
                       'power_rms': None,
                       'Particle vs. Time': data[i]}
    return data, parameters


def get_time_results(filepath: Path,
                     e_acc: list[float],
                     delimiter: str = '\t',
                     ) -> tuple[dict, np.ndarray]:
    r"""
    Get population evolution, auto export from SPARK3D.

    Precise an output directory in the SPARK3D command-line, look for
    ``time_results.txt``.

    Parameters
    ----------
    filepath : Path
        Path to the file to be loaded.
    e_acc : list[float]
        List of accelerating field values in MV/m.
    delimiter : str, optional
        Delimiter between columns. The default is ``\\t``.

    Returns
    -------
    data : dict
        Holds evolution of electron population with time in ns.
    parameters : np.ndarray
        Array of accelerating fields in V/m.

    """
    parameters = np.array(e_acc) * 1e6
    raw_data = np.loadtxt(filepath)
    # Convert s into ns
    raw_data[:, 2] *= 1e9
    data = {}

    # We get the different simulations and sort them by their simulation number
    # (first column)
    for i in range(1, len(e_acc) + 1):
        idx = np.where(raw_data[:, 0] == float(i))
        pop_evol = raw_data[idx[0], 2:4]
        power_rms = raw_data[idx[0], 1][0]

        data[i] = {'E_acc in MV per m': e_acc[i - 1],
                   'power_rms': power_rms,
                   'Particle vs. Time': pop_evol}
    return data, parameters
