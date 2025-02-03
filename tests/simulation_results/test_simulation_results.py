"""Define tests for the ABC :class:`.SimulationResults`."""

import numpy as np
import pytest

from simultipac.simulation_results.simulation_results import (
    ShapeMismatchError,
    SimulationResults,
)


def test_simulation_results_initialization() -> None:
    """Check proper instantiation of object."""
    time = np.array([0, 1, 2, 3])
    population = np.array([1000, 1200, 1500, 10000])
    result = SimulationResults(
        id=1, e_acc=5.0, p_rms=2.0, time=time, population=population
    )

    assert result.id == 1
    assert result.e_acc == 5.0
    assert result.p_rms == 2.0
    assert np.array_equal(result.time, time)
    assert np.array_equal(result.population, population)


def test_trim_trailing() -> None:
    """Check that trailing trails."""
    time = np.array([0, 1, 2, 3, 4, 5, 6])
    population = np.array([1000, 200, 1, 0, 0, 0, 0])
    result = SimulationResults(
        id=2,
        e_acc=10.0,
        p_rms=None,
        time=time,
        population=population,
        trim_trailing=True,
    )
    expected_time = time[:3]
    expected_population = population[:3]
    assert np.array_equal(result.time, expected_time)
    assert np.array_equal(result.population, expected_population)


def test_no_trim_when_population_nonzero() -> None:
    """Check that no trailing occurs when populations does not reach 0."""
    time = np.array([0, 1, 2, 3, 4, 5, 6])
    population = np.array([1000, 2000, 3000, 10000, 100, 5, 1])
    result = SimulationResults(
        id=3,
        e_acc=7.5,
        p_rms=1.0,
        time=time,
        population=population,
        trim_trailing=True,
    )

    assert np.array_equal(result.population, population)
    assert np.array_equal(result.time, time)


def test_shape_mismatch_error() -> None:
    """Check that an error is raised if population and time have different shape."""
    time = np.array([0, 1, 2, 3])
    population = np.array([1000, 1200, 1500])  # Last point is missing
    with pytest.raises(ShapeMismatchError):
        SimulationResults(
            id=4, e_acc=5.0, p_rms=2.0, time=time, population=population
        )
