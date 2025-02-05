r"""Define exponential growth model as well as fitting function.

Other approaches that have been tried:
.. note::
    Other models that I tried:

    .. math::
        N(t) = N_0 (1 + K \\cos{(\\omega_0 t + \\phi_0)}) \\mathrm{e}^{\\alpha t}

        N(t) = N_0 (1 + K \\cos{(\\omega_0 t / T_{MP} + \\phi_0)})
        \\mathrm{e}^{\\alpha t}

    I dropped them as with too much unkowns, any model can fit anything.

"""

import logging
import math
import warnings
from collections.abc import Callable
from typing import TypedDict

import numpy as np
from scipy.ndimage import uniform_filter1d
from scipy.optimize import OptimizeWarning, curve_fit

warnings.simplefilter("error", OptimizeWarning)


class ExpGrowthParameters(TypedDict):
    """Define parameters for exp growth."""

    n_0: float
    alpha: float
    t_0: float


def exp_growth(
    time: np.ndarray,
    n_0: float,
    alpha: float,
    t_0: float = 0.0,
    **kwargs,
) -> np.ndarray:
    """Exponential growth factor function.

    .. math::
        N(t) = N_0 \\mathrm{e}^{\\alpha (t-t_0)}

    Parameters
    ----------
    time : np.ndarray
        Time in ns.
    n_0 : float
        Number of electrons at the start of the exponential growth.
    alpha : float
        Exponential growth factor in 1/ns.
    t_0 : float, optional
        Time at which the exponential growth starts, in ns. The default is 0.0.

    Returns
    -------
    population : np.ndarray
        Modelled population evolution. It is filled with NaN for times before
        ``t_0``.

    """
    population = np.full(len(time), np.nan)
    after_t_0 = np.where(time >= t_0)
    population[after_t_0] = n_0 * np.exp(alpha * (time[after_t_0] - t_0))
    return population


def exp_growth_log(
    time: np.ndarray,
    n_0: float,
    alpha: float,
    t_0: float = 0.0,
    **kwargs,
) -> np.ndarray:
    r"""Exponential growth factor function, in log form.

    .. math::
        \\log{N(t)} = \log{N_0} + \\alpha (t-t_0)

    In general, better results for the fit process than the classic
    :func:``exp_growth``.

    Parameters
    ----------
    time : np.ndarray
        Time in ns.
    n_0 : float
        Number of electrons at the start of the exponential growth.
    alpha : float
        Exponential growth factor in 1/ns.
    t_0 : float, optional
        Time at which the exponential growth starts, in ns. The default is 0.0.

    Returns
    -------
    log_population : np.ndarray
        Log of modelled population evolution. It is filled with NaN for times
        before ``t_0``.

    """
    log_population = np.full(len(time), np.nan)
    log_population[np.where(time >= t_0)] = math.log(n_0) + alpha * (
        time - t_0
    )
    return log_population


def fit_alpha(
    time: np.ndarray,
    population: np.ndarray,
    fitting_range: float,
    period: float,
    running_mean: bool = True,
    minimum_final_number_of_electrons: int = 0,
    bounds: tuple[list[float], list[float]] = ([1e-10, -10.0], [np.inf, 10.0]),
    initial_values: list[float | None] = [None, -9.0],
    log_fit: bool = True,
) -> ExpGrowthParameters:
    """Perform the exponential growth fitting.

    Parameters
    ----------
    time : np.ndarray
        Time in ns.
    population : np.ndarray
        Evolution of electron population with time.
    fitting_range : float
        Time over which the exp growth is searched. Longer is better, but you
        do not want to start the fit before the exp growth starts.
    running_mean : bool, optional
        To tell if you want to average the number of particles over one period.
        Highly recommended. The default is True.
    minimum_final_number_of_electrons : int, optional
        Under this final number of electrons, we do no bother finding the exp
        growth factor and return a ``NaN``.
    bounds : tuple[list[float], list[float]], optional
        Upper bound and lower bound for the two variables: initial number of
        electrons, exp growth factor.
    initial_values: list[float | None], optional
        Initial values for the two variables: initial number of electrons, exp
        growth factor.
    log_fit : bool, optional
        To perform the fit on :func:`exp_growth_log` rather than
        :func:`exp_growth`. The default is True, as it generally shows better
        convergence.

    Returns
    -------
    fit_parameters : ExpGrowthParameters
        Holds the fit parameters.

    """
    fit_parameters = ExpGrowthParameters(n_0=np.nan, alpha=np.nan, t_0=np.nan)
    n_points = len(time)
    if len(population) != n_points:
        raise ValueError(f"{len(time) = } while {len(population) = }")

    if final_number := population[-1] < minimum_final_number_of_electrons:
        logging.debug(
            f"{final_number = } while {minimum_final_number_of_electrons = }. "
            "We return alpha = NaN."
        )
        return fit_parameters

    fit_args = _to_fit(time, population, fitting_range, log_fit=log_fit)
    fit_func, fit_time, fit_pop = fit_args

    if running_mean:
        width = _n_points_in_a_period(fit_time, period)
        population = _smoothen(fit_pop, width)

    if initial_values[0] is None:
        initial_values[0] = fit_pop[0]
    if initial_values[0] < bounds[0][0]:
        initial_values[0] = bounds[0][0]

    try:
        result = curve_fit(
            fit_func,
            fit_time,
            fit_pop,
            p0=initial_values,
            bounds=bounds,
            maxfev=5000,
        )[0]

    except OptimizeWarning as e:
        logging.info(f"Fit failed, returnin NaN parameters.\n{e}")
        return fit_parameters

    fit_parameters = ExpGrowthParameters(
        n_0=result[0], alpha=result[1], t_0=fit_time[0]
    )
    return fit_parameters


def _to_fit(
    time: np.ndarray,
    population: np.ndarray,
    fitting_range: float,
    log_fit: bool = True,
) -> tuple[Callable, np.ndarray, np.ndarray]:
    """Determine the ``x``, ``f(x)`` arrays as well as ``f`` for the fit.

    Parameters
    ----------
    time : np.ndarray
        Full array of times.
    population : np.ndarray
        Corresponding population evolution,
    fitting_range : float
        Time over which the exp growth is searched. Longer is better, but you
        do not want to start the fit before the exp growth starts.
    log_fit : bool, optional
        To perform the fit on :func:`exp_growth_log` rather than
        :func:`exp_growth`. The default is True, as it generally shows better
        convergence.

    Returns
    -------
    fit_func : Callable
        The ``f`` we want to retrieve parameters.
    fit_time : np.ndarray
        The ``x`` values for the fit.
    fit_pop : np.ndarray
        The ``f(x)`` we will try to retrieve.

    """

    indexes = _indexes_for_fit(time, population, fitting_range)

    fit_time = time[indexes]
    fit_pop = population[indexes]
    if not log_fit:
        return exp_growth, fit_time, fit_pop

    return (
        exp_growth_log,
        fit_time,
        np.log(fit_pop),
    )


def _indexes_for_fit(
    time: np.ndarray,
    population: np.ndarray,
    fitting_range: float,
    minimum_number_of_points: int = 5,
) -> range:
    """Determine the indexes on which the fit should be performed.

    The fit is performed over ``fitting_range``, ending at the last non-zero
    population count.

    """
    if fitting_range <= 0.0:
        raise ValueError(f"Cannot perform a fit on {fitting_range = }")
    idx_end = np.where(population == 0)[0][0]
    final_time = float(time[idx_end])

    start_time = final_time - fitting_range
    if start_time < 0.0:
        logging.warning("Fitting range is larger than simulation time")
    idx_start = np.argmin(np.abs(time - start_time))

    if not isinstance(idx_start, int):
        idx_start = int(idx_start)

    if (n_fit_points := idx_end - idx_start) < minimum_number_of_points:
        logging.warning(
            f"Fit performed on {n_fit_points} data points, which may be too "
            "low. This usually happens when time is given in seconds instead "
            f"of nanoseconds. Does {final_time = } seems right? What about "
            f"{fitting_range = }?"
        )
    logging.debug(f"Fit will be performed from index {idx_start} to {idx_end}")
    return range(idx_start, idx_end + 1)


def _n_points_in_a_period(
    time: np.ndarray, period: float, min_points_per_period: int = 5
) -> int:
    """Get the number of data points in a single RF period.

    Print a warning if the number of points is lower than
    ``min_points_per_period``.

    """
    n_points = np.argmin(np.abs(time - period))
    if not isinstance(n_points, int):
        n_points = int(n_points)
    if n_points < min_points_per_period:
        logging.warning(
            f"There are {n_points} data points per RF period, which may be too "
            " low for the running mean routine. Maybe time (final value: "
            f"{time[-1]}) and {period = } have different units?"
        )
    return n_points


def _smoothen(population: np.ndarray, width: int) -> np.ndarray:
    """Smooth data (running mean).

    See also: https://stackoverflow.com/a/43200476/12188681

    .. todo::
        Better unit testing for this function.

    """
    # Old implementation, kept if needed
    # https://stackoverflow.com/a/43200476/12188681
    # run = uniform_filter1d(np.log(data[:, 1]), size=i_width,
    #                        mode='nearest')
    # # We do the running mean on the log to center the running metric on the
    # # oscillations
    # data_to_fit = np.column_stack((data[:, 0], run))
    # # data_to_fit = data_to_fit[idx_start:i_remove]
    # data_to_fit = data_to_fit[idx_start:idx_end + 1]\
    return uniform_filter1d(population, size=width, mode="nearest")
