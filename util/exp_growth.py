#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 17:32:09 2023.

@author: placais

Module to store the exponential growth models, perform fit.
Currently, only exponential growth model is implemented:
    N(t) = N_0 * exp(alfa * t)

Other approaches that have been tried:
    N(t) = N_0 * (1 + K * cos(omega_0 * t + phi)) * exp(alfa * t)
    N(t) = N_0 * (1 + K * cos(omega_0 * t / MPperiod + phi)) * exp(alfa * t)
I dropped it as with too much unkowns, any model can fit anything.
"""

import warnings
import numpy as np
from scipy.optimize import curve_fit, OptimizeWarning
from scipy.ndimage import uniform_filter1d

from multipactor.helper.helper import printc

warnings.simplefilter("error", OptimizeWarning)


# =============================================================================
# Called by user
# =============================================================================
def fit_all(str_model: str, d_data: dict, map_id: dict, key_part: str,
            period: float,
            fitting_range: float, running_mean: bool = True):
    """Perform the exponential growth fit over all set of parameters."""
    for key, val in d_data.items():
        modelled, fit_parameters = _fit_single(str_model, val[key_part],
                                               period, fitting_range)

        val[f"{key_part} (model)"] = modelled
        if fit_parameters is None:
            print(f"Skipped {map_id[key]}")
            val['alfa (model)'] = np.NaN
            continue

        # Keep only what really interests us
        val["alfa (model)"] = fit_parameters[1]


def fit_all_spark(str_model: str, d_data: dict, key_part: str,
                  fitting_range: float, running_mean: bool = True):
    """Perform the exponential growth fit over all set of parameters."""
    key_eacc = 'E_acc in MV per m'
    for key, val in d_data.items():
        modelled, fit_parameters = _fit_single_spark(str_model, val[key_part],
                                                     fitting_range)

        val[f"{key_part} (model)"] = modelled
        if fit_parameters is None:
            print(f"Skipped {val[key_eacc]}")
            val['alfa (model)'] = np.NaN
            continue

        # Keep only what really interests us
        val["alfa (model)"] = fit_parameters[1]


# =============================================================================
# Definition of exp growth models   # TODO: clean this, too cumbersome...
# =============================================================================
def _select_model(str_model: str):
    """Return proper functions, number of arguments, bounds, etc."""
    assert str_model in ["classic"]

    model = _model_1
    model_log = _model_1_log
    model_printer = _model_1_printer
    n_args = 2
    #          N_0    alfa
    bounds = ([1e-10, -10.],
              [np.inf, 10.])
    initial_values = [None, 0.]

    return model, model_log, model_printer, n_args, bounds, initial_values


def _model_1(time: np.array, *args) -> np.array:
    """Exponential growth model."""
    return args[0] * np.exp(args[1] * time)


def _model_1_log(time: np.array, *args) -> np.array:
    """Exponential growth model but in log."""
    return np.log(args[0]) + args[1] * time


def _model_1_printer(*args):
    """Pretty print the parameters."""
    print("Optimized with:")
    print(f"\tN_0   = {args[0]}")
    print(f"\talfa  = {args[1]} 1/ns")


# =============================================================================
# Actual fit function
# =============================================================================
def _fit_single(str_model: str, data: np.array, period: float,
                fitting_range: float, running_mean: bool = True,
                print_fit_parameters: bool = False):
    """
    Perform the exponential growth fitting on a single parameter.

    Parameters
    ----------
    str_model : str
        Indicates what exp growth model should be used.
    data : np.array
        Holds time in ns in first column, number of electrons in second.
    period : float
        RF period in ns.
    fitting_range : float
        Time over which the exp growth is searched. Longer is better, but you
        do not want to start the fit before the exp growth starts.
    running_mean : bool, optional
        To tell if you want to average the number of particles over one period.
        Hihgly recommended. The default is True.
    print_fit_parameters : bool, optional
        To tell if you want to output the fitting parameters when they are
        found. The default is False.

    Returns
    -------
    modelled : np.array
        Holds time in first column, modelled number of electrons in second.
    fit_parameters : tuple or None
        Holds all exp growth model parameters, as well as the time at which the
        fit starts. If no MP, fit_parameters is None
    """
    model, model_log, model_printer, n_args, bounds, initial_values \
        = _select_model(str_model)

    modelled = np.full(data.shape, np.NaN)
    modelled[:, 0] = data[:, 0]

    # If obvious no MP, we skip
    # if data[-1, 1] < 10.:
        # return modelled, None

    idx_end = np.where(data[:, 1])[0][-1]
    t_start = data[idx_end, 0] - fitting_range
    if t_start < 0.:
        printc("exp_growth._fit_single warning:", "fitting range larger",
               "than simulation time!")
    idx_start = np.argmin(np.abs(data[:, 0] - t_start))
    data_to_fit = np.column_stack((data[idx_start:idx_end + 1, 0],
                                   np.log(data[idx_start:idx_end + 1, 1])))

    # i_remove = None
    if running_mean:
        # We get the number of points spanning over one period
        i_width = np.argmin(np.abs(data[:, 0] - period))
        if i_width < 5:
            print("Warning! i_width is too small. Check that period and" +
                  " data[:, 0] have same units. Consider also reducing the" +
                  "fitting range.")
        # We do not use the last points
        # i_remove = -int(i_width / 2)

        # https://stackoverflow.com/a/43200476/12188681
        # run = uniform_filter1d(np.log(data[:, 1]), size=i_width,
        #                        mode='nearest')
        # # We do the running mean on the log to center the running metric on the
        # # oscillations
        # data_to_fit = np.column_stack((data[:, 0], run))
        # # data_to_fit = data_to_fit[idx_start:i_remove]
        # data_to_fit = data_to_fit[idx_start:idx_end + 1]\
        data_to_fit[:, 1] = uniform_filter1d(data_to_fit[:, 1], size=i_width,
                                             mode='nearest')

    try:
        initial_values[0] = data_to_fit[0, 0]
        if initial_values[0] < bounds[0][0]:
            initial_values[0] = bounds[0][0]
        result = curve_fit(model_log, data_to_fit[:, 0], data_to_fit[:, 1],
                           p0=initial_values, bounds=bounds, maxfev=5000)[0]

    except OptimizeWarning:
        result = np.full((n_args), np.NaN)

    # Fit parameters
    if print_fit_parameters:
        model_printer(*result)

    # modelled[idx_start:i_remove, 1] = model(data_to_fit[:, 0], *result)
    modelled[idx_start:idx_end + 1, 1] = model(data_to_fit[:, 0], *result)

    return modelled, (*result, t_start)


def _fit_single_spark(str_model: str, data: np.array, fitting_range: float,
                      print_fit_parameters: bool = False):
    """
    Perform the exponential growth fitting on a single parameter.

    Parameters
    ----------
    str_model : str
        Indicates what exp growth model should be used.
    data : np.array
        Holds time in ns in first column, number of electrons in second.
    fitting_range : float
        Time over which the exp growth is searched. Longer is better, but you
        do not want to start the fit before the exp growth starts.
    print_fit_parameters : bool, optional
        To tell if you want to output the fitting parameters when they are
        found. The default is False.

    Returns
    -------
    modelled : np.array
        Holds time in first column, modelled number of electrons in second.
    fit_parameters : tuple or None
        Holds all exp growth model parameters, as well as the time at which the
        fit starts. If no MP, fit_parameters is None
    """
    model, model_log, model_printer, n_args, bounds, initial_values \
        = _select_model(str_model)

    modelled = np.full(data.shape, np.NaN)
    modelled[:, 0] = data[:, 0]

    # Ignore population = 0:
    # t_end = data[-1, 0]
    # if data[-1, 1]
    # if data[-1, 1] < 1.:
        # return modelled, None

    idx_end = np.where(data[:, 1])[0][-1]
    t_start = data[idx_end, 0] - fitting_range
    if t_start < 0.:
        printc("exp_growth._fit_single_spark warning:", "fitting range larger",
               "than simulation time!")
    idx_start = np.argmin(np.abs(data[:, 0] - t_start))
    data_to_fit = np.column_stack((data[idx_start:idx_end + 1, 0],
                                   np.log(data[idx_start:idx_end + 1, 1])))

    try:
        initial_values[0] = data_to_fit[0, 0]
        if initial_values[0] < bounds[0][0]:
            initial_values[0] = bounds[0][0]
        # initial_values = [None, None]
        result = curve_fit(model_log, data_to_fit[:, 0], data_to_fit[:, 1],
                           p0=initial_values,
                           bounds=bounds, maxfev=5000)[0]

    except OptimizeWarning:
        result = np.full((n_args), np.NaN)

    # Fit parameters
    if print_fit_parameters:
        model_printer(*result)

    modelled[idx_start:idx_end + 1, 1] = model(data_to_fit[:, 0], *result)

    return modelled, (*result, t_start)
