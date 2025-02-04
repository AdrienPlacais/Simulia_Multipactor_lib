r"""Define exponential growth models as well as fitting functions.

Currently, only one exponential growth model is implemented:

.. math::
    N(t) = N_0 \\mathrm{e}^{\\alpha t}

Other approaches that have been tried:

.. math::
    N(t) = N_0 (1 + K \\cos{(\\omega_0 t + \\phi_0)}) \\mathrm{e}^{\\alpha t}

    N(t) = N_0 (1 + K \\cos{(\\omega_0 t / T_{MP} + \\phi_0)})
    \\mathrm{e}^{\\alpha t}

I dropped it as with too much unkowns, any model can fit anything.

"""

import logging
import warnings

import numpy as np
from scipy.ndimage import uniform_filter1d
from scipy.optimize import OptimizeWarning, curve_fit

warnings.simplefilter("error", OptimizeWarning)


# =============================================================================
# Called by user
# =============================================================================
def fit_all(
    str_model: str,
    data: dict,
    map_id: dict,
    key_part: str,
    period: float,
    fitting_range: float,
    running_mean: bool = True,
):
    """Perform the exponential growth fit over all set of parameters."""
    for key, val in data.items():
        modelled, fit_parameters = _fit_single(
            str_model, val[key_part], period, fitting_range
        )

        val[f"{key_part} (model)"] = modelled
        if fit_parameters is None:
            logging.info(f"Skipped {map_id[key]}")
            val["alpha (model)"] = np.nan
            continue

        # Keep only what really interests us
        val["alpha (model)"] = fit_parameters[1]


def fit_all_spark(
    str_model: str,
    complete_population_evolutions: dict,
    key_eacc: str,
    key_part: str,
    fitting_range: float,
    period: float,
    running_mean: bool = True,
):
    """Perform the exponential growth fit over all set of parameters."""
    for population_evolution in complete_population_evolutions.values():
        modelled, fit_parameters = _fit_single_spark(
            str_model,
            population_evolution[key_part],
            fitting_range,
            period,
            e_acc=population_evolution[key_eacc],
        )

        population_evolution[f"{key_part} (model)"] = modelled
        if fit_parameters is None:
            logging.info(f"Skipped {population_evolution[key_eacc]}")
            population_evolution["alpha (model)"] = np.nan
            continue

        # Keep only what really interests us
        population_evolution["alpha (model)"] = fit_parameters[1]


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
    #          N_0    alpha
    bounds = ([1e-10, -10.0], [np.inf, 10.0])
    initial_values = [None, -9.0]

    return model, model_log, model_printer, n_args, bounds, initial_values


def _model_1(time: np.array, *args) -> np.array:
    """Exponential growth model."""
    return args[0] * np.exp(args[1] * time)


def _model_1_log(time: np.array, *args) -> np.array:
    """Exponential growth model but in log."""
    return np.log(args[0]) + args[1] * time


def _model_1_printer(*args):
    """Pretty print the parameters."""
    logging.info("Optimized with:")
    logging.info(f"\tN_0   = {args[0]}")
    logging.info(f"\talpha  = {args[1]} 1/ns")


# =============================================================================
# Actual fit function
# =============================================================================
def _fit_single(
    str_model: str,
    data: np.array,
    period: float,
    fitting_range: float,
    running_mean: bool = True,
    print_fit_parameters: bool = False,
    skip_obvious: bool = True,
) -> tuple[np.ndarray, tuple[float, ...] | None]:
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
        Highly recommended. The default is True.
    print_fit_parameters : bool, optional
        To tell if you want to output the fitting parameters when they are
        found. The default is False.
    skip_obvious : bool, optional
        When True, we do not bother trying to fit exponential growth if the
        number of electrons at the end of simulation is less than 10. The
        default is True.

    Returns
    -------
    modelled : np.ndarray
        Holds time in first column, modelled number of electrons in second. It
        has the same shape as ``data``, but number of particles is full of nan
        before the start of the fit.
    fit_parameters : tuple[float, ...] | None
        First elements of the tuple are the fitting constants. Last element is
        the time at which the fit starts. If fit was unsuccessful, returns None
        instead.

    """
    model, model_log, model_printer, n_args, bounds, initial_values = (
        _select_model(str_model)
    )

    modelled = np.full(data.shape, np.nan)
    modelled[:, 0] = data[:, 0]

    if skip_obvious and data[-1, 1] < 10.0:
        return modelled, None

    idx_end = np.where(data[:, 1])[0][-1]
    t_start = data[idx_end, 0] - fitting_range
    if t_start < 0.0:
        logging.warning("Fitting range larger than simulation time!")
    idx_start = np.argmin(np.abs(data[:, 0] - t_start))
    data_to_fit = np.column_stack(
        (
            data[idx_start : idx_end + 1, 0],
            np.log(data[idx_start : idx_end + 1, 1]),
        )
    )

    # i_remove = None
    if running_mean:
        # We get the number of points spanning over one period
        i_width = np.argmin(np.abs(data[:, 0] - period))
        if i_width < 5:
            logging.warning(
                "i_width is too small. Check that period and data[:, 0] have "
                "same units. Consider reducing the fitting range."
            )

        # https://stackoverflow.com/a/43200476/12188681
        # run = uniform_filter1d(np.log(data[:, 1]), size=i_width,
        #                        mode='nearest')
        # # We do the running mean on the log to center the running metric on the
        # # oscillations
        # data_to_fit = np.column_stack((data[:, 0], run))
        # # data_to_fit = data_to_fit[idx_start:i_remove]
        # data_to_fit = data_to_fit[idx_start:idx_end + 1]\
        data_to_fit[:, 1] = uniform_filter1d(
            data_to_fit[:, 1], size=i_width, mode="nearest"
        )

    try:
        initial_values[0] = data_to_fit[0, 0]
        if initial_values[0] < bounds[0][0]:
            initial_values[0] = bounds[0][0]
        result = curve_fit(
            model_log,
            data_to_fit[:, 0],
            data_to_fit[:, 1],
            p0=initial_values,
            bounds=bounds,
            maxfev=5000,
        )[0]

    except OptimizeWarning:
        result = np.full((n_args), np.nan)

    # Fit parameters
    if print_fit_parameters:
        model_printer(*result)

    modelled[idx_start : idx_end + 1, 1] = model(data_to_fit[:, 0], *result)

    return modelled, (*result, t_start)


def _fit_single_spark(
    str_model: str,
    population_evolution: np.ndarray,
    fitting_range: float,
    period: float,
    print_fit_parameters: bool = False,
    e_acc: float | None = None,
):
    """
    Perform the exponential growth fitting on a single parameter.

    Parameters
    ----------
    str_model : str
        Indicates what exp growth model should be used.
    population_evolution : np.array
        Holds time in ns in first column, number of electrons in second.
    fitting_range : float
        Time over which the exp growth is searched. Longer is better, but you
        do not want to start the fit before the exp growth starts.
    period : float
        Signal period.
    print_fit_parameters : bool, optional
        To tell if you want to output the fitting parameters when they are
        found. The default is False.

    Returns
    -------
    modelled : np.array
        Holds time in first column, modelled number of electrons in second.
    fit_parameters : tuple or None
        Holds all exp growth model parameters, as well as the time at which the
        fit starts. If no MP, fit_parameters is None.

    """
    model, model_log, model_printer, n_args, bounds, initial_values = (
        _select_model(str_model)
    )

    modelled = np.full(population_evolution.shape, np.nan)
    modelled[:, 0] = population_evolution[:, 0]

    # Ignore population = 0:
    # t_end = population_evolution[-1, 0]
    # if population_evolution[-1, 1]
    # if population_evolution[-1, 1] < 1.:
    # return modelled, None

    idx_end = np.where(population_evolution[:, 1])[0][-1]

    # For SWELL baked
    if True:
        # we want to avoid fitting on the end of the decay
        idx_end = min(
            idx_end, np.argmin(np.abs(population_evolution[:, 1] - 10.0))
        )
        logging.info(idx_end, e_acc)

    t_start = population_evolution[idx_end, 0] - fitting_range

    t_lim = 5.0 * period
    if t_start < t_lim:
        logging.warning(
            f"E_acc={e_acc:.2e} fitting range too large w.r.t simulation time!"
            f" I set it to a higher value {t_lim:2f}ns."
        )
        t_start = t_lim

    idx_start = np.argmin(np.abs(population_evolution[:, 0] - t_start))
    population_evolution_to_fit = np.column_stack(
        (
            population_evolution[idx_start : idx_end + 1, 0],
            np.log(population_evolution[idx_start : idx_end + 1, 1]),
        )
    )

    try:
        initial_values[0] = population_evolution_to_fit[0, 0]
        if initial_values[0] < bounds[0][0]:
            initial_values[0] = bounds[0][0]
        # initial_values = [None, None]
        result = curve_fit(
            model_log,
            population_evolution_to_fit[:, 0],
            population_evolution_to_fit[:, 1],
            p0=initial_values,
            bounds=bounds,
            maxfev=5000,
        )[0]

    except OptimizeWarning:
        result = np.full((n_args), np.nan)
    except IndexError:
        result = np.full((n_args), np.nan)

    # Fit parameters
    if print_fit_parameters:
        model_printer(*result)

    modelled[idx_start : idx_end + 1, 1] = model(
        population_evolution_to_fit[:, 0], *result
    )

    return modelled, (*result, t_start)
