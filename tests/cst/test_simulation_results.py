"""Test the correct behavior of :class:`.CSTResults` and its factory."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from simultipac.cst.simulation_results import (
    CSTResults,
    CSTResultsFactory,
    MissingFileError,
)


def test_cst_results_initialization() -> None:
    """Test initialization of :class:`.CSTResults` object."""
    time = np.array([0, 1, 2, 3])
    population = np.array([10, 8, 5, 0])
    parameters = {"B_field": 1.2, "n_steps": 100}
    result = CSTResults(
        id=1,
        e_acc=5.0,
        p_rms=2.0,
        time=time,
        population=population,
        parameters=parameters,
    )

    assert result.id == 1
    assert result.e_acc == 5.0
    assert result.p_rms == 2.0
    assert result.parameters == parameters
    assert np.array_equal(result.time, time)
    assert np.array_equal(result.population, population)


def test_cst_results_factory_mandatory_files() -> None:
    """
    Test that the :class:`.CSTResultsFactory` correctly lists mandatory files.

    """
    factory = CSTResultsFactory()
    assert factory.mandatory_files == (
        "E_acc in MV per m.txt",
        "Parameters.txt",
        "Particle vs. Time.txt",
    )


def test_cst_results_factory_missing_file(mocker: MagicMock) -> None:
    """Test that MissingFileError is raised when a mandatory file is missing."""
    factory = CSTResultsFactory()
    mocker.patch("simultipac.cst.simulation_results.get_id", return_value=1)
    mocker.patch(
        "simultipac.cst.simulation_results.mmdd_xxxxxxx_folder_to_dict",
        return_value={},
    )

    with pytest.raises(MissingFileError):
        factory._from_simulation_folder(Path("dummy_folder"))


def test_cst_results_factory_from_simulation_folder(mocker: MagicMock) -> None:
    """Test the _from_simulation_folder method of :class:`.CSTResultsFactory`."""
    factory = CSTResultsFactory()
    mock_raw_results = {
        "E_acc in MV per m": 5.0,
        "Particle vs. Time": np.array([[0, 1000], [1, 900], [2, 500]]),
        "Parameters": {"B_field": 1.2},
    }

    mocker.patch(
        "simultipac.cst.simulation_results.get_id",
        return_value=1,
    )
    mocker.patch(
        "simultipac.cst.simulation_results.mmdd_xxxxxxx_folder_to_dict",
        return_value=mock_raw_results,
    )
    result = factory._from_simulation_folder(Path("dummy_folder"))

    assert result.id == 1
    assert result.e_acc == 5.0
    assert np.array_equal(result.time, [0, 1, 2])
    assert np.array_equal(result.population, [1000, 900, 500])
