#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  9 10:25:07 2023.

@author: placais

In this module we define functions to load data from SPARK3D.

.. note::
    In ``complete_population_evolutions`` returned by the loading functions,
    keys are unique integers corresponding to a simulation. With SPARK3D, they
    start at 0 and are ordered.
    This is only for consistency with CST, which gives random ID number to
    every simulation.

"""
from pathlib import Path

import numpy as np


def load_population_evolution(filepath: Path,
                              e_acc: np.ndarray,
                              key_part: str = 'Particle vs. Time',
                              key_eacc: str = 'E_acc in MV per m',
                              key_power: str = 'power_rms',
                              **kwargs,
                              ) -> tuple[dict, np.ndarray]:
    """Get population evolution data from SPARK3D simulation.

    We infer the format of the data from the extension of ``filepath``. If it
    is ``.csv``, it is expected that you manually exported the data. If it is
    ``.txt``, it is expected that you called SPARK3D from the command line and
    provide the path to the ``time_results.txt`` file that is produced.

    Parameters
    ----------
    filepath : Path
        Path to the file to be loaded.
    e_acc : np.ndarray
        Accelerating field values in MV/m.
    delimiter : str, optional
        Delimiter between columns. The default is a space.
    key_part : str, optional
        The name of the particle vs time entry in the output dictionaries. The
        default is 'Particle vs. Time'.
    key_eacc : str, optional
        The name of the accelerating field entry in the output dictionaries.
        The default is 'E_acc in MV per m'.
    key_power : str, optional
        The name of the RMS power entry in the output dictionaries. The default
        is 'power_rms'.

    Returns
    -------
    complete_population_evolutions : dict[int, dict[str, np.ndarray | float |\
None]]
        Holds evolution of electron population with time in ns. Keys are unique
        integers, values are other dict holding accelerating field, evolution
        of population with time.
    parameters : np.ndarray
        Array of accelerating fields in V/m.

    """
    filetype = filepath.suffix
    if filetype == ".txt":
        return _get_population_evolution_txt(filepath,
                                             e_acc,
                                             key_part=key_part,
                                             key_eacc=key_eacc,
                                             key_power=key_power,
                                             **kwargs)
    if filetype == ".csv":
        return _get_population_evolution_csv(filepath,
                                             e_acc,
                                             key_part=key_part,
                                             key_eacc=key_eacc,
                                             key_power=key_power,
                                             **kwargs)
    raise IOError(f"{filetype = } not recognized.")


def _get_population_evolution_csv(filepath: Path,
                                  e_acc: np.ndarray,
                                  key_part: str,
                                  key_eacc: str,
                                  key_power: str,
                                  delimiter: str = ' ',
                                  ) -> tuple[dict, np.ndarray]:
    """Get population evolution data from a SPARK3D manual export.

    Right-click on ``Multipactor results``, ``Export to CSV``.

    """
    raw_data = np.loadtxt(filepath, delimiter=delimiter)

    parameters = np.array(e_acc) * 1e6
    n_param = len(e_acc)

    # Create a list of arrays
    population_evolutions = [np.column_stack((raw_data[:, 0] * 1e9,
                             raw_data[:, i]))
                             for i in range(1, n_param + 1)]

    # For consistency with CST import, we remove the end of MP simulations
    # (population = 0)
    for i, population_evolution in enumerate(population_evolutions):
        idx_to_remove = np.argwhere(population_evolution[:, 1] == 0.)
        if idx_to_remove.size > 0:
            last_idx = idx_to_remove[0][0]
            population_evolutions[i] = population_evolution[:last_idx]

    complete_population_evolutions = {
        i: {key_eacc: single_e_acc,
            key_power: None,
            key_part: population_evolution,
            }
        for i, (single_e_acc, population_evolution)
        in enumerate(zip(e_acc, population_evolutions))
    }
    return complete_population_evolutions, parameters


def _get_population_evolution_txt(filepath: Path,
                                  e_acc: np.ndarray,
                                  key_part: str,
                                  key_eacc: str,
                                  key_power: str,
                                  delimiter: str = '\t',
                                  ) -> tuple[dict, np.ndarray]:
    r"""
    Get population evolution, auto export from SPARK3D.

    Precise an output directory in the SPARK3D command-line, look for
    ``time_results.txt``.

    """
    parameters = np.array(e_acc) * 1e6
    population_evolutions = np.loadtxt(filepath, delimiter=delimiter)
    # Convert s into ns
    population_evolutions[:, 2] *= 1e9
    complete_population_evolutions = {}

    # We get the different simulations and sort them by their simulation number
    # (first column)
    for i in range(1, len(e_acc) + 1):
        idx = np.where(population_evolutions[:, 0] == float(i))
        pop_evol = population_evolutions[idx[0], 2:4]
        power_rms = population_evolutions[idx[0], 1][0]

        complete_population_evolutions[i] = {
            key_eacc: e_acc[i - 1],
            key_power: power_rms,
            key_part: pop_evol}
    return complete_population_evolutions, parameters
