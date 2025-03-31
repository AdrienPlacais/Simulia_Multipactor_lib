"""Test the correct behavior of :class:`.CSTResultsFactory`."""

from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pytest

from simultipac.cst.simulation_results import (
    CSTResultsFactory,
    MissingFileError,
)


def test_mandatory_files() -> None:
    """
    Test that the :class:`.CSTResultsFactory` correctly lists mandatory files.

    """
    factory = CSTResultsFactory(e_acc_parameter=("key1",))
    assert factory.mandatory_files == {
        "Parameters.txt",
        "Particle vs. Time.txt",
    }


def test_mandatory_files_no_e_acc_in_params() -> None:
    """
    Test that the :class:`.CSTResultsFactory` correctly lists mandatory files.

    """
    factory = CSTResultsFactory(e_acc_parameter=())
    assert factory.mandatory_files == {
        "E_acc in MV per m.txt",
        "Parameters.txt",
        "Particle vs. Time.txt",
    }


def test_get_e_acc_from_parameters(
    mocker: MagicMock,
) -> None:
    """Test that accelerating field can be found in :file:`Parameters.txt`."""
    factory = CSTResultsFactory(e_acc_parameter=("dummy_acc",))
    factory._parameters_file = "dummy_param.txt"

    e_acc = 42.0
    mock_raw_results = {
        "a": 3.0,
        "dummy_param": {"b": 5.0, "dummy_acc": e_acc},
        "c": -1.0,
    }
    mock_debug = mocker.patch("logging.debug")
    assert factory._pop_e_acc(mock_raw_results, Path("dummy")) == e_acc
    mock_debug.assert_called_once()


def test_get_e_acc_from_file(mocker: MagicMock) -> None:
    """Test that accelerating field can be found in dedicated file."""
    factory = CSTResultsFactory(
        e_acc_parameter=(), e_acc_file_mv_m="dummy_file.txt"
    )
    factory._parameters_file = "dummy_param.txt"

    e_acc = 42.0
    mock_raw_results = {
        "a": 3.0,
        "dummy_file": e_acc * 1e6,
        "dummy_param": {"b": 5.0},
        "c": -1.0,
    }
    mock_debug = mocker.patch("logging.debug")
    assert factory._pop_e_acc(mock_raw_results, Path("dummy")) == e_acc
    mock_debug.assert_called_once()


def test_get_e_acc_not_found() -> None:
    """Test that error is raised when e_acc could not be found."""
    factory = CSTResultsFactory(
        e_acc_parameter=("key_1", "key_2"), e_acc_file_mv_m="dummy_file.txt"
    )
    factory._parameters_file = "dummy_param.txt"

    e_acc = 42.0
    mock_raw_results = {
        "a": 3.0,
        "dummy_file_with_typo": e_acc,
        "dummy_param": {"key_1_with_typo": e_acc},
        "c": -1.0,
    }
    with pytest.raises(ValueError):
        factory._pop_e_acc(mock_raw_results, Path("dummy"))


@pytest.mark.implementation
def test_missing_file(mocker: MagicMock) -> None:
    """Test that MissingFileError is raised when a mandatory file is missing."""
    factory = CSTResultsFactory()
    mocker.patch.multiple(
        "simultipac.cst.simulation_results",
        get_id=mocker.Mock(return_value=1),
        mmdd_xxxxxxx_folder_to_dict=mocker.Mock(return_value={}),
    )

    with pytest.raises(MissingFileError):
        factory._from_simulation_folder(Path("dummy_folder"))


@pytest.mark.implementation
def test_from_simulation_folder(mocker: MagicMock) -> None:
    """Test the _from_simulation_folder method of :class:`.CSTResultsFactory`."""
    factory = CSTResultsFactory()
    mock_raw_results = {
        "Particle vs. Time": np.array([[0, 1000], [1, 900], [2, 500]]),
        "Parameters": {"B_field": 1.2},
    }

    mocker.patch.multiple(
        "simultipac.cst.simulation_results",
        get_id=mocker.Mock(return_value=1),
        mmdd_xxxxxxx_folder_to_dict=mocker.Mock(return_value=mock_raw_results),
    )
    e_acc = 42.0
    mocker.patch.object(factory, "_pop_e_acc", return_value=e_acc)
    result = factory._from_simulation_folder(Path("dummy_folder"))

    assert result.id == 1
    assert result.e_acc == e_acc
    assert np.array_equal(result.time, [0, 1, 2])
    assert np.array_equal(result.population, [1000, 900, 500])
