#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  9 10:25:07 2023.

@author: placais

This module holds all the functions to import CST data. There is two main
functions:
    - get_parameter_sweep_auto_export works with the Template Based
      Post-Processing 'Save Export Folder during Parameter Sweep' (one folder
      per set of parameters, in which several quantities may be stored).
    - get_parameter_sweep_manual works with the manual Import/Export button
      (one file per quantity, set of parameters are written in comments).

@TODO: evaluate expressions such as "param2 = 2 * param1"

Needs Python 3.7+ as uses ordering of dicts
https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
"""

import os
import itertools as it
import ast
import numpy as np


def get_parameter_sweep_auto_export(
        folderpath: str, delimiter: str = '\t') -> dict:
    """
    Get parameter sweep data from a CST automatic Post-Processing ASCII export.

    In Template Based Post-Processing : General 1D > ASCII Export > what you
    want (one for each data).
    After the last ASCII Export :
    Template Based Post-Processing > Misc > Save Export Folder during Parameter
    Sweep

    This way, all exported ASCII data are in
    Project/Export_Parametric/mmdd-xxxxxxx folders.

    Parameters
    ----------
    folderpath : str
        Path to the folder where the mmdd-xxxxxxx folders are located.
    delimiter : str, optional
        Delimiter between columns

    Returns
    -------
    d_data : dict
        Holds all the exported data for every set of parameters.
    """
    d_data = {}
    l_folders = os.listdir(folderpath)
    l_keys = [folder.split('-')[-1] for folder in l_folders]

    for folder, key in zip(l_folders, l_keys):
        folder = os.path.join(folderpath, folder)
        d_data[int(key)] = _get_single_parameter_auto_export(folder, delimiter)
    return d_data


def _map_param_to_id(d_data: dict, *args, sort: bool = False) -> dict:
    """Associate ids (d_data key entries) to specific parameters."""
    map_id = {}

    for _id in d_data.keys():
        params = []
        for param in args:
            val = d_data[_id]['Parameters'][param]
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
                              for i, _ in enumerate(args)])
                         )
                  }
    return map_id


def full_map_param_to_id(d_data: dict, *args) -> (dict, dict):
    """Also return corresponding param values."""
    # We get the sorted mapping of data
    map_id = _map_param_to_id(d_data, *args, sort=True)

    # We get every unique value of parameters
    d_uniques = {arg: list(dict.fromkeys([val[i]
                                          for val in map_id.values()]))
                 for i, arg in enumerate(args)}
    return map_id, d_uniques


def get_id(map_id: list, *args) -> int:
    """Give correct id."""
    for key, val in map_id.items():
        if val == [arg for arg in args]:
            return key
    return -1


def get_values(
        d_data: dict, key_data: str, *args, to_numpy: bool = True,
        warn_missing: bool = False, ins_param: bool = False) \
        -> np.array:
    """Return a n-dim numpy array containing (key_)data sorted by args."""
    # We get the sorted mapping of data and the unique values for each
    # parameter
    map_id, d_uniques = full_map_param_to_id(d_data, *args)

    # Generate all combinations of parameters
    _lp = [vals for vals in d_uniques.values()]
    comb = [p for p in it.product(*_lp)]

    # Create an empty array
    out = [np.NaN for i in range(len(comb))]

    # Look for data for every combination of parameters
    for i, __c in enumerate(comb):
        _id = get_id(map_id, *__c)

        if _id == -1:
            if warn_missing:
                print(f"Warning! No value found for the parameters {__c}.")
            continue

        out[i] = d_data[_id][key_data]

    # Reshape
    new_shape = [len(val) for val in d_uniques.values()]
    out = np.reshape(np.asarray(out, dtype=object), new_shape)

    # We add values of the parameters in the first column, row, for easier data
    # manipulation
    if ins_param:
        if len(args) == 1:
            out = np.column_stack((_lp[0], out))
        elif(len(args) == 2):
            new_out = np.full([x + 1 for x in new_shape], np.NaN, dtype=object)
            new_out[1:, 0] = _lp[0]
            new_out[0, 1:] = _lp[1]
            new_out[1:, 1:] = out
            out = new_out
        elif(len(args) == 3):
            new_out = np.full([x + 1 for x in new_shape], np.NaN, dtype=object)
            new_out[1:, 0, 0] = _lp[0]
            new_out[0, 1:, 0] = _lp[1]
            new_out[0, 0, 1:] = _lp[2]
            new_out[1:, 1:, 1:] = out
            out = new_out
        else:
            # TODO
            raise IOError("Param value insertion not implemented for dim>3.")

    if not to_numpy:
        return out.tolist()
    return out


def _get_single_parameter_auto_export(folderpath: str, delimiter: str) -> dict:
    """Load all the data into a single mmdd-xxxxxxx folder."""
    dic = {}

    # Recursively load every file
    for root, _, files in os.walk(folderpath):
        # Skip 3d data
        if os.path.split(root)[-1] == '3d':
            continue

        for file in files:
            full_path = os.path.join(root, file)
            file = os.path.splitext(file)[0]

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


def _parameters_file_to_dict(filepath: str) -> dict:
    """Special treatment for the 'Parameters.txt' file."""
    d_parameters = {}
    with open(filepath, 'r') as file:
        for line in file:
            line = line.split('=')
            d_parameters[line[0]] = line[1].strip()

    # Convert strings into float if possible
    for key, val in d_parameters.items():
        try:
            d_parameters[key] = float(val)
        except ValueError:
            continue

    return d_parameters


def get_parameter_sweep_manual(filepath: str, key: str = None,
                               delimiter: str = '\t') -> list:
    """
    Get parameter sweep data from a CST manual ASCII export.

    Tables > 1D Results > what you want. Then
    Post-Processing ribbon > Import/Export > Plot Data (ASCII)

    Parameters
    ----------
    filepat : str
        Path to the file to be loaded.
    key : str, optional
        Sort the parameters dict by a key.
    delimiter : str, optional
        Delimiter between columns

    Returns
    -------
    data : list
        Holds evolution of the data with time.
    parameters : list of dict or np.array
        Dictionary of all parameters. If key is provided, it returns the value
        of this key instead.
    """
    data = []
    data_this_param = []
    parameters = []

    with open(filepath, 'r') as file:
        for line in file:
            if line[:11] == "#Parameters":
                parameters.append(_str_to_dict(line))

                # If not first iteration, save data from preceedent iteration
                if len(data_this_param) > 0:
                    data.append(np.array(data_this_param))
                data_this_param = []

            if line[0] == '#':
                continue

            data_this_param.append([float(line.split(delimiter)[0]),
                                    float(line.split(delimiter)[1])])

    # Handle last data of array
    data.append(np.array(data_this_param))

    # Check that key is here
    if not(key is None or key in parameters[0]):
        print(f"Warning! key {key} not found in the file.")
        print("Script will continue anyway.")
        key = None

    # We return only the value of the desired key
    if key is not None:
        parameters = np.array([param[key] for param in parameters])
        idx = np.argsort(parameters)

        parameters = parameters[idx]
        data = [data[i] for i in idx]

    return data, parameters


def _str_to_dict(parameters: str) -> dict:
    """Convert the string Parameters to a dict."""
    # Remove useless
    parameters = parameters[14:]
    parameters = parameters.replace('=', '" : ')
    parameters = parameters.replace('; ', ', "')
    parameters = parameters.replace('{', '{"')

    # Convert string into actual dict
    parameters = ast.literal_eval(parameters)
    return parameters
