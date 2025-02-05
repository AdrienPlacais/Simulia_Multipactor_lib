"""Test the exponential growth fitting suite."""

import logging
from unittest.mock import MagicMock

import numpy as np
import pytest

from simultipac.util.exponential_growth import (
    ExpGrowthParameters,
    _indexes_for_fit,
    _n_points_in_a_period,
    _smoothen,
    _to_fit,
    exp_growth,
    exp_growth_log,
    fit_alpha,
)


def test_indexes_for_fit_no_multipactor() -> None:
    """Test _indexes_for_fit function."""
    time = np.linspace(0, 10, 11)
    #                          |===============| fitting range
    population = np.array([10, 10, 9, 5, 3, 2, 1, 0, 0, 0, 0])

    indexes = _indexes_for_fit(
        time, population, fitting_range=5.0, minimum_number_of_points=0
    )

    assert [i for i in indexes] == [1, 2, 3, 4, 5, 6]


def test_indexes_for_fit_with_multipactor() -> None:
    """Test _indexes_for_fit function."""
    time = np.linspace(0, 10, 11)
    #                            fitting range |======================|
    population = np.array([10, 10, 9, 5, 3, 2, 1, 10, 100, 1000, 10000])

    indexes = _indexes_for_fit(
        time, population, fitting_range=4.0, minimum_number_of_points=0
    )

    assert [i for i in indexes] == [6, 7, 8, 9, 10]


def test_indexes_for_fit_fitting_larger_than_simulation_warning(
    mocker: MagicMock,
) -> None:
    """Test that a warning is raised if fitting range too big wrt sim time."""
    time = np.linspace(0, 10, 11)
    #                  |===========| fitting range
    population = np.array([10, 10, 5, 0, 0, 0, 0, 0, 0, 0, 0])
    mock_warning = mocker.patch("logging.warning")

    indexes = _indexes_for_fit(
        time, population, fitting_range=5.0, minimum_number_of_points=0
    )

    assert [i for i in indexes] == [0, 1, 2]
    mock_warning.assert_called_once()


def test_indexes_for_fit_fitting_not_enough_points_warning(
    mocker: MagicMock,
) -> None:
    """Test that a warning is raised if not enough points."""
    time = np.linspace(0, 10, 11)
    #                      |=======| fitting range
    population = np.array([10, 10, 5, 0, 0, 0, 0, 0, 0, 0, 0])
    mock_warning = mocker.patch("logging.warning")

    indexes = _indexes_for_fit(
        time, population, fitting_range=2.0, minimum_number_of_points=5
    )

    assert [i for i in indexes] == [0, 1, 2]
    mock_warning.assert_called_once()


def test_indexes_for_fit_negative_fit_range() -> None:
    """Test _indexes_for_fit function."""
    time = np.linspace(0, 10, 11)
    population = np.array([10, 10, 9, 5, 3, 2, 1, 0, 0, 0, 0])

    with pytest.raises(ValueError):
        _indexes_for_fit(
            time, population, fitting_range=0.0, minimum_number_of_points=0
        )


def test_n_points_in_a_period() -> None:
    """Test _n_points_in_a_period function."""
    points_per_period = 10
    periods = 100
    period = 1.0
    time = np.linspace(0, periods * period, periods * points_per_period)

    n_points = _n_points_in_a_period(time, period)

    assert n_points == points_per_period


def test_n_points_in_a_period_not_enough_points(mocker: MagicMock) -> None:
    """Test _n_points_in_a_period function."""
    points_per_period = 10
    periods = 100
    period = 1.0
    time = np.linspace(0, periods * period, periods * points_per_period)
    mock_warning = mocker.patch("logging.warning")

    n_points = _n_points_in_a_period(time, period, min_points_per_period=11)

    assert n_points == points_per_period
    mock_warning.assert_called_once()


def test_smoothen() -> None:
    """Test _smoothen function."""
    population = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    smoothed = _smoothen(population, width=3)
    assert smoothed.shape == population.shape


def test_to_fit(mocker: MagicMock) -> None:
    """Test _to_fit function."""
    time = np.linspace(0, 10, 100)
    population = exp_growth(time, 2.0, 0.3)

    mock_indexes = range(20, 80)
    mocker.patch(
        "simultipac.util.exponential_growth._indexes_for_fit",
        return_value=mock_indexes,
    )
    expected_fit_time = time[mock_indexes]
    expected_fit_pop = population[mock_indexes]

    fit_func, fit_time, fit_pop = _to_fit(
        time, population, fitting_range=1.0, log_fit=False
    )
    assert callable(fit_func)
    np.testing.assert_array_equal(fit_time, expected_fit_time)
    np.testing.assert_array_equal(fit_pop, expected_fit_pop)


def test_exp_growth() -> None:
    """Test exponential growth function."""
    time = np.array([0, 1, 2, 3, 4, 5])
    n_0 = 1.0
    alpha = 0.5
    expected = n_0 * np.exp(alpha * time)
    result = exp_growth(time, n_0, alpha)
    np.testing.assert_allclose(result, expected, rtol=1e-5, equal_nan=True)


def test_exp_growth_with_t0() -> None:
    """Test exponential growth function with t_0 shift."""
    time = np.array([0, 1, 2, 3, 4, 5])
    n_0 = 1.0
    alpha = 0.5
    t_0 = 2.0
    expected = np.full_like(time, np.nan, dtype=float)
    expected[time >= t_0] = n_0 * np.exp(alpha * (time[time >= t_0] - t_0))
    result = exp_growth(time, n_0, alpha, t_0)
    np.testing.assert_allclose(result, expected, rtol=1e-5, equal_nan=True)


def test_exp_growth_log() -> None:
    """Test logarithmic exponential growth function."""
    time = np.array([0, 1, 2, 3, 4, 5])
    n_0 = 1.0
    alpha = 0.5
    expected = np.full_like(time, np.nan, dtype=float)
    expected[time >= 0] = np.log(n_0) + alpha * time[time >= 0]
    result = exp_growth_log(time, n_0, alpha)
    np.testing.assert_allclose(result, expected, rtol=1e-5, equal_nan=True)


def test_fit_alpha(mocker: MagicMock) -> None:
    """Test fitting of exponential growth parameters."""
    n_points = 100
    time = np.linspace(0, 10, n_points)
    n_0 = 2.0
    alpha = 0.3
    population = exp_growth(time, n_0, alpha)

    mocker.patch(
        "simultipac.util.exponential_growth._to_fit",
        return_value=(exp_growth_log, time, np.log(population)),
    )

    fit_params = fit_alpha(
        time,
        population,
        fitting_range=5.0,
        period=1.0,
        running_mean=False,
        log_fit=True,
    )
    np.testing.assert_allclose(
        [fit_params["n_0"], fit_params["alpha"]], [n_0, alpha]
    )


def test_fit_alpha_no_log(mocker: MagicMock) -> None:
    """Test fitting of exponential growth parameters (not log_fit)."""
    n_points = 100
    time = np.linspace(0, 10, n_points)
    n_0 = 2.0
    alpha = 0.3
    population = exp_growth(time, n_0, alpha)

    mocker.patch(
        "simultipac.util.exponential_growth._to_fit",
        return_value=(exp_growth, time, population),
    )

    fit_params = fit_alpha(
        time,
        population,
        fitting_range=5.0,
        period=1.0,
        log_fit=False,
        running_mean=False,
    )
    np.testing.assert_allclose(
        [fit_params["n_0"], fit_params["alpha"]], [n_0, alpha]
    )


def test_fit_alpha_size_mismatch() -> None:
    """Test error is raised if time and pop have different length."""
    n_points = 100
    time = np.linspace(0, 10, n_points)
    n_0 = 2.0
    alpha = 0.3
    population = exp_growth(time[:-1], n_0, alpha)

    with pytest.raises(ValueError):
        fit_alpha(time, population, fitting_range=5.0, period=1.0)
