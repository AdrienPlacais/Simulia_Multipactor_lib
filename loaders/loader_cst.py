#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Define all the functions to import CST data.

The main function is :func:`get_parameter_sweep_auto_export`. It works with the
Template Based Post-Processing ``Save Export Folder during Parameter Sweep``
(one folder per set of parameters, in which several quantities may be stored).

Needs Python 3.7+ as uses ordering of dicts
https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value

.. note::
    As for now, it can only load data stored in a single file. For Position
    Monitor exports (one file = one time step), see dedicated package
    ``PositionMonitor``.

.. todo::
    Evaluate expressions such as ``param2 = 2 * param1``

"""
import ast
import itertools as it
import os
from pathlib import Path
from typing import Any

import numpy as np

from multipactor.helper.helper import printc


# =============================================================================
# Actual loaders
# =============================================================================
def get_parameter_sweep_auto_export(
        folderpath: Path,
        delimiter: str = '\t'
) -> dict[int, dict[str, float | np.ndarray | dict[str, float | str]]]:
    r"""
    Get parameter sweep data from a CST automatic Post-Processing ASCII export.

    In Template Based Post-Processing:
    ``General 1D > ASCII Export > what you want (one for each data)``.
    After the last ASCII Export :
    ``Template Based Post-Processing > Misc > Save Export Folder during
    Parameter Sweep``

    This way, all exported ASCII data are in
    ``Project/Export_Parametric/mmdd-xxxxxxx`` folders.

    Parameters
    ----------
    folderpath : Path
        Path to the folder where the ``mmdd-xxxxxxx`` folders are located.
    delimiter : str, optional
        Delimiter between columns. The default is ``\t``.

    Returns
    -------
    data : dict[int, dict[str, float | np.ndarray | dict[str, float | str]]]
        Holds all the exported data for every set of parameters. Keys are the
        ID of each simulation (the seven-digits number in the corresponding
        folder name). Values are dictionaries as returned by
        :func:`_get_single_parameter_auto_export`.

    """
    data = {}
    folders = list(folderpath.iterdir())
    keys = [str(folder).split('-')[-1] for folder in folders]

    for folder, key in zip(folders, keys):
        data[int(key)] = _get_single_parameter_auto_export(folder, delimiter)
    return data


def _get_single_parameter_auto_export(folderpath: Path,
                                      delimiter: str) -> dict[str, Any]:
    """
    Load all the data stored into a single ``mmdd-xxxxxxx`` folder.

    Parameters
    ----------
    folderpath : Path
        ``mmdd-xxxxxx`` folder from which all files will be loaded.
    delimiter : str
        Delimiter between two columns.

    Returns
    -------
    dic : dict[str, Any]
        Dictionary holding all exported data. Keys are the name of the data,
        values the corresponding value. The Parameters dict is also stored.

    """
    dic = {}

    # Recursively load every file
    for root, _, files in os.walk(folderpath):
        # Skip 3d data
        if os.path.split(root)[-1] == '3d':
            continue

        for file in files:
            full_path = Path(root, file)
            file = full_path.stem

            # Skip hidden files
            if file[0] == '.':
                continue

            if file == 'Parameters':
                dic[file] = _parameters_file_to_dict(full_path)
                continue
            data = np.loadtxt(full_path, delimiter=delimiter)

            if data.shape == ():
                data = float(data)
            dic[file] = data

    return dic


def _parameters_file_to_dict(filepath: Path) -> dict[str, float | str]:
    """
    Load the ``Parameters.txt`` file.

    .. todo::
        Detect integer values

    .. todo::
        Evaluate simple expressions. A parameter defined as '1/2' will be a
        string instead of 0.5 (float)...

    Parameters
    ----------
    filepath : Path
        Path to the file.

    Returns
    -------
    parameters : dict[str, float | str]
        Holds the name of the Parameter as a key, and the corresponding value
        as a value.

    """
    parameters = {}
    with open(filepath, 'r') as file:
        for line in file:
            line = line.split('=')
            parameters[line[0]] = line[1].strip()

    # Convert strings into float if possible
    for key, val in parameters.items():
        try:
            parameters[key] = float(val)
        except ValueError:
            continue

    return parameters


# =============================================================================
# Link a simulation with a set of parameters
# =============================================================================
def full_map_param_to_id(data: dict, *parameters: str
                         ) -> tuple[dict[int, list[float]],
                                    dict[str, list[float]]]:
    """
    Link simulation ID to parameters values, get unique parameters values.

    Parameters
    ----------
    data : dict
        Full data dict as returned by :func:`get_parameter_sweep_auto_export`.
    *parameters : str
        The parameters under study.

    Returns
    -------
    map_id : dict[int, list[float]]
        A dictionary linking simulation ID to parameters values. The keys are
        the ID of the simulations. The values are the values of the parameters
        corresponding to the simulation ID.
    uniques : dict[str, list[float]]
        Dictionary holding all unique values of each parameter. Keys are name
        of the parameters parameters. Values are a list of the unique values;
        should be of length 1 for each parameter that did not evolve during
        simulation.

    """
    map_id = _map_param_to_id(data, *parameters, sort=True)

    uniques = {arg: list(dict.fromkeys([val[i] for val in map_id.values()]))
               for i, arg in enumerate(parameters)}
    return map_id, uniques


def _map_param_to_id(data: dict, *parameters: str, sort: bool = False
                     ) -> dict[int, list[float]]:
    """
    Associate ids (data key entries) to specific parameter values.

    Parameters
    ----------
    data : dict
        Full data dict as returned by :func:`get_parameter_sweep_auto_export`.
    *parameters: str
        The parameters to be mapped.
    sort : bool, optional
        To tell if the output should be sorted by increasing parameter values.
        The default is False.

    Returns
    -------
    map_id : dict[int, list[float]]
        A dictionary linking simulation ID to parameters values. The keys are
        the ID of the simulations. The values are the values of the parameters
        corresponding to the simulation ID.

    """
    map_id = {}

    for _id in data.keys():
        params = []
        for param in parameters:
            val = data[_id]['Parameters'][param]
            if isinstance(val, str):
                val = ast.literal_eval(val)
            params.append(val)
        map_id[_id] = params

    # If necessary, sort by increasing value on each parameter
    # https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
    if sort:
        map_id = {k: v for k, v in
                  sorted(map_id.items(),
                         key=lambda item: tuple(
                             [item[1][i]
                              for i, _ in enumerate(parameters)])
                         )
                  }
    return map_id


def get_id(map_id: dict[int, list[float]], *parameters_vals: float) -> int:
    """
    Give ID of simulation that was realized with the set ``parameters_vals``.

    Parameters
    ----------
    map_id : dict[int, list[float]]
        A dictionary linking simulation ID to parameters values. The keys are
        the ID of the simulations. The values are the values of the
        ``parameters`` corresponding to the simulation ID. As returned by
        :func:`_map_param_to_id`.
    *parameters_vals : float
        Values of the parameters.

    Returns
    -------
    simul_id : int
        ID of the simulation realized with the set of parameters values
        ``parameters_vals``.

    """
    for simul_id, simul_param_vals in map_id.items():
        if simul_param_vals == [val for val in parameters_vals]:
            return simul_id
    return -1


# =============================================================================
# Actual values getter
# =============================================================================
def get_values(data: dict[int, dict[str, Any]],
               key_data: str,
               *parameters: str,
               to_numpy: bool = True,
               warn_missing: bool = False,
               ins_param: bool = False) -> np.ndarray:
    """
    Return a n-dim numpy array containing data sorted by parameters.

    Parameters
    ----------
    data : dict[int, dict[str, Any]]
        Dict holding all data as returned by
        :func:`get_parameter_sweep_auto_export`.
    key_data : str
        Key to the data you want (should be a filename in
        ``Export_Parametric/mmdd-xxxxxxx`` folders).
    *parameters : str
        Keys to against which parameter ``key_data`` should be sorted (should
        be in ``Parameters.txt``).
    to_numpy : bool, optional
        Return the data as a numpy array. The default is True.
    warn_missing : bool, optional
        Raise a warning if there is no data for some combinations of
        parameters. The default is False.
    ins_param : bool, optional
        Tells if the value of the parameters defined by ``parameters`` should
        be INSerted in the first axis. The default is False.

    Raises
    ------
    NotImplementedError
        Raised when the number of parameters is too high.

    Returns
    -------
    out : np.ndarray
        Array holding ``key_data``, sorted by combination of ``parameters``.
        If ``ins_param``, first line of every axis holds parameter value.
        If ``not to_numpy``, out is converted to a list.

    """
    map_id, uniques = full_map_param_to_id(data, *parameters)
    parameters_unique_values = [vals for vals in uniques.values()]
    combinations_of_param_vals = [p
                                  for p in it.product(
                                      *parameters_unique_values)]

    out = [np.NaN for i in range(len(combinations_of_param_vals))]

    for i, __c in enumerate(combinations_of_param_vals):
        _id = get_id(map_id, *__c)

        if _id == -1:
            if warn_missing:
                printc("loader_cst.get_values warning", "no value found for",
                       f"the parameters {__c}.")
            continue

        out[i] = data[_id][key_data]

    new_shape = [len(val) for val in uniques.values()]
    if len(out) != new_shape[0] and len(new_shape) > 1:
        out = np.reshape(np.asarray(out, dtype=object), new_shape)

    if ins_param:
        out = _insert_parameters_values(out, parameters_unique_values)

    if not to_numpy:
        return out.tolist()
    return out


def _insert_parameters_values(out: np.ndarray,
                              parameters_unique_values: list[list[float]],
                              ) -> np.ndarray:
    """
    Insert the values of the parameters in first row of every dimension.

    .. todo::
        Handle number of parameters > 3.

    .. todo::
        Not very Pythonic...

    Parameters
    ----------
    out : np.ndarray
        Value asked by user.
    parameters_unique_values : list[list[float]]
        Unique values of the parameters, to be inserted.

    Returns
    -------
    new_out : np.ndarray
        ``out`` but with parameters unique values in each first row/column/etc.

    Raises
    ------
    NotImplementedError :
        When the number of parameters if higher than three.

    """
    n_parameters = len(parameters_unique_values)
    shape = out.shape
    if n_parameters == 1:
        new_out = np.full((shape[0] + 1, 2), np.NaN, dtype=object)
        new_out[1:, 0] = parameters_unique_values[0]
        new_out[1:, 1] = out
        return new_out

    if n_parameters == 2:
        new_out = np.full([x + 1 for x in shape], np.NaN, dtype=object)
        new_out[1:, 0] = parameters_unique_values[0]
        new_out[0, 1:] = parameters_unique_values[1]
        new_out[1:, 1:] = out
        return new_out

    if n_parameters == 3:
        new_out = np.full([x + 1 for x in shape], np.NaN, dtype=object)
        new_out[1:, 0, 0] = parameters_unique_values[0]
        new_out[0, 1:, 0] = parameters_unique_values[1]
        new_out[0, 0, 1:] = parameters_unique_values[2]
        new_out[1:, 1:, 1:] = out
        return new_out

    raise NotImplementedError("Too much parameters.",
                              "Parameter value insertion not implemented for "
                              " more than three parameters.")


# =============================================================================
# More specific loaders
# =============================================================================
def particle_monitor(filepath: Path,
                     delimiter: str | None = None
                     ) -> tuple[tuple[float | int]]:
    """Load a single Particle Monitor file."""
    n_header = 6

    with open(filepath, 'r', encoding='utf-8') as file:
        particles_info = tuple(tuple(line.split(delimiter))
                               for i, line in enumerate(file)
                               if i > n_header)

    return particles_info
