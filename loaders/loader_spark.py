#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  9 10:25:07 2023.

@author: placais
"""

import numpy as np


def get_population_evolution(filepath: str, e_acc: list, delimiter: str = ' ',
                             to_numpy: bool = False) -> list:
    """
    Get population evolution data from a SPARK3D export.

    Parameters
    ----------
    filepath : str
        Path to the file to be loaded.
    e_acc : list
        List of accelerating field values in MV/m.
    delimiter : str, optional
        Delimiter between columns

    Returns
    -------
    data : list
        Holds evolution of electron population with time in ns.
    parameters : np.array
        Array of accelerating fields in V/m.
    """
    raw_data = np.loadtxt(filepath, delimiter=' ')

    parameters = np.array(e_acc) * 1e6
    n_param = len(e_acc)

    # Create a list of arrays
    data = [np.column_stack((raw_data[:, 0] * 1e9, raw_data[:, i]))
            for i in range(1, n_param + 1)]

    # For consistency with CST import, we remove the end of MP simulations
    # (population = 0)
    for i in range(n_param):
        dat = data[i]
        idx = np.argwhere(dat[:, 1] == 0.)
        if idx.size > 0:
            data[i] = dat[:idx[0][0], :]
    return data, parameters
