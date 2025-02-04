"""Test :class:`.Spark3DResults` and :class:`.Spark3DResultsFactory`."""

from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pytest

from simultipac.spark3d.simulation_results import (
    Spark3DResults,
    Spark3DResultsFactory,
)


def test_spark3d_results_initialization() -> None:
    """Check that direct instantiation works."""
    time = np.array([0, 1, 2, 3], dtype=np.float64)
    population = np.array([10, 8, 5, 0], dtype=np.float64)
    result = Spark3DResults(
        id=1, e_acc=5e6, p_rms=2.0, time=time, population=population
    )

    assert result.id == 1
    assert result.e_acc == 5e6
    assert result.p_rms == 2.0
    assert np.array_equal(result.time, time)
    assert np.array_equal(result.population, population)


def test_spark3d_results_factory_from_txt(mocker: MagicMock) -> None:
    """Test instantiation from a fake ``TXT`` file."""
    factory = Spark3DResultsFactory()
    mock_data = np.array(
        [
            [1, 100, 0, 1000],
            [1, 100, 1, 1010],
            [2, 50, 0, 1000],
            [2, 50, 1, 900],
        ],
        dtype=np.float64,
    )
    mocker.patch("numpy.loadtxt", return_value=mock_data)

    e_acc = np.array([1e6, 2e6])
    results = factory._from_txt(Path("dummy.txt"), e_acc, delimiter=" ")

    assert len(results) == 2
    assert results[0].id == 1
    assert results[0].e_acc == 1e6
    assert np.array_equal(results[0].time, [0, 1e9])
    assert np.array_equal(results[0].population, [1000, 1010])


def test_spark3d_results_factory_from_csv(mocker: MagicMock) -> None:
    """Test instantiation from a fake ``CSV`` file."""
    factory = Spark3DResultsFactory()
    mock_data = np.array(
        [
            [0, 1000, 1000],
            [1e-9, 1010, 900],
            [2e-9, 1020, 500],
        ]
    )
    mocker.patch("numpy.loadtxt", return_value=mock_data)

    e_acc = np.array([1e6, 2e6])
    results = factory._from_csv(Path("dummy.csv"), e_acc, delimiter=" ")

    assert len(results) == 2
    assert results[0].id == 1
    assert results[0].e_acc == 1e6
    assert np.array_equal(results[0].time, [0, 1, 2])
    assert np.array_equal(results[0].population, [1000, 1010, 1020])


def test_spark3d_results_factory_from_csv_with_trim(mocker: MagicMock) -> None:
    """Test instantiation from a fake ``CSV`` file."""
    factory = Spark3DResultsFactory()
    mock_data = np.array(
        [
            [0, 1000, 1000],
            [1e-9, 1010, 900],
            [2e-9, 1020, 0],
        ],
        dtype=np.float64,
    )
    mocker.patch("numpy.loadtxt", return_value=mock_data)

    e_acc = np.array([1e6, 2e6])
    results = factory._from_csv(Path("dummy.csv"), e_acc, delimiter=" ")

    assert len(results) == 2
    assert results[1].id == 2
    assert results[1].e_acc == 2e6
    assert np.array_equal(results[1].time, [0, 1])
    assert np.array_equal(results[1].population, [1000, 900])
