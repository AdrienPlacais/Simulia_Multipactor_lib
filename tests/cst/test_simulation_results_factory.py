"""Test the correct behavior of :class:`.CSTResultsFactory`."""

from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pytest

from simultipac.cst.simulation_results import (
    CSTResultsFactory,
    MissingFileError,
)
from simultipac.types import E_ACC_UNIT_t


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

    mock_raw_results = {
        "a": 3.0,
        "dummy_file": 42.0,
        "dummy_param": {"b": 5.0},
        "c": -1.0,
    }
    mock_debug = mocker.patch("logging.debug")
    assert factory._pop_e_acc(
        mock_raw_results, Path("dummy")
    ) == pytest.approx(42e6)
    mock_debug.assert_called_once()


@pytest.mark.parametrize(
    "unit,factor", [("V/m", 1.0), ("kV/m", 1e3), ("MV/m", 1e6)]
)
def test_get_e_acc_from_parameters_unit(
    unit: E_ACC_UNIT_t, factor: float
) -> None:
    """Test that the unit of :file:`Parameters.txt` is taken into account."""
    factory = CSTResultsFactory(
        e_acc_parameter=("dummy_acc",), e_acc_unit=unit
    )
    factory._parameters_file = "dummy_param.txt"
    mock_raw_results = {"dummy_param": {"dummy_acc": 2.0}}
    returned = factory._pop_e_acc(mock_raw_results, Path("dummy"))
    assert returned == pytest.approx(2.0 * factor)


def test_get_e_acc_from_file_unit() -> None:
    """Test that the unit of the dedicated file is taken into account."""
    factory = CSTResultsFactory(
        e_acc_parameter=(),
        e_acc_file_mv_m="dummy_file.txt",
        e_acc_file_unit="kV/m",
    )
    factory._parameters_file = "dummy_param.txt"
    mock_raw_results = {"dummy_file": 2.0, "dummy_param": {}}
    returned = factory._pop_e_acc(mock_raw_results, Path("dummy"))
    assert returned == pytest.approx(2e3)


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


def test_missing_file(mocker: MagicMock, tmp_path: Path) -> None:
    """Test that MissingFileError is raised when a mandatory file is missing."""
    factory = CSTResultsFactory()
    mocker.patch.multiple(
        "simultipac.cst.simulation_results",
        get_id=mocker.Mock(return_value=1),
        mmdd_xxxxxxx_folder_to_dict=mocker.Mock(return_value={}),
    )

    with pytest.raises(MissingFileError):
        factory.from_simulation_folder(tmp_path)


def test_from_simulation_folder(mocker: MagicMock, tmp_path: Path) -> None:
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
    result = factory.from_simulation_folder(tmp_path)

    assert result.id == 1
    assert result.e_acc == e_acc
    assert np.array_equal(result.time, [0, 1, 2])
    assert np.array_equal(result.population, [1000, 900, 500])


def test_get_e_acc_expression_warns_and_falls_back(mocker: MagicMock) -> None:
    """Test that an unevaluated expression is skipped with a warning."""
    factory = CSTResultsFactory(
        e_acc_parameter=("dummy_acc",), e_acc_file_mv_m="dummy_file.txt"
    )
    factory._parameters_file = "dummy_param.txt"
    mock_raw_results = {
        "dummy_file": 3.0,
        "dummy_param": {"dummy_acc": "2*3"},
    }
    mock_warning = mocker.patch("logging.warning")
    returned = factory._pop_e_acc(mock_raw_results, Path("dummy"))
    assert returned == pytest.approx(3e6)
    mock_warning.assert_called_once()
