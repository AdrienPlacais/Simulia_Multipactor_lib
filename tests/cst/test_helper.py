"""Test the helper functions from the CST module."""

from pathlib import Path
from unittest.mock import mock_open, patch

import numpy as np
import pytest

from simultipac.cst.helper import (
    _parameters_file_to_dict,
    get_id,
    mmdd_xxxxxxx_folder_to_dict,
)


def test_acceptable_id() -> None:
    """Check that a normally constitued folder name leads to good id."""
    folderpath = Path("/path/to/my/simu/0420-1234567")
    id = get_id(folderpath)
    assert id == 1234567


def test_unacceptable_id() -> None:
    """Check that an error is raised if the simulation folder is invalid."""
    folderpath = Path("C:/Users/Michel/Downloads/Avis Imposition 2006.pdf")
    with pytest.raises(ValueError):
        get_id(folderpath)


def test_normal_parameters_file_to_dict() -> None:
    """Test that a classic :file:`Parameters.txt` leads to normal dict."""
    mock_file_content = """float=3.0e+06
int_converted_to_float=1
    """
    expected = {"float": 3.0e06, "int_converted_to_float": 1.0}
    with patch("builtins.open", mock_open(read_data=mock_file_content)):
        assert _parameters_file_to_dict(Path("dummy.txt")) == expected


def test_parameters_file_to_dict_with_unconvertible_data() -> None:
    """Test that a debug message is printed if unconvertible data was found."""
    mock_file_content = """f=1e9
T=1/f
half=1/2
    """
    expected = {"f": 1e9, "T": "1/f", "half": "1/2"}
    with (
        patch("builtins.open", mock_open(read_data=mock_file_content)),
        patch("logging.debug") as mock_debug,
    ):
        assert _parameters_file_to_dict(Path("dummy.txt")) == expected
        assert mock_debug.call_count == 2


def test_mmdd_xxxxxxx_3d_files_are_skipped() -> None:
    """Check that ``mmdd_xx`` loading does not load 3d data."""
    mock_foldercontent = [
        ("mmdd-xxxxxxx", ["Particle Info [PIC]", "3d"], []),
        ("mmdd-xxxxxxx/Particle Info [PIC]", [], []),
        ("mmdd-xxxxxxx/3d", [], ["e_field.m3d", "b_field.m3d"]),
    ]
    with (
        patch("os.walk", return_value=mock_foldercontent),
        patch("logging.debug") as mock_debug,
        patch("logging.info") as mock_info,
    ):
        mmdd_xxxxxxx_folder_to_dict(Path("/path/to/dummy/"))
        assert mock_debug.call_count == 2
        mock_info.assert_called_once()


def test_mmdd_xxxxxxx_hidden_files_are_skipped() -> None:
    """Check that hidden files are not loaded."""
    mock_foldercontent = [
        ("mmdd-xxxxxxx", ["Particle Info [PIC]"], [".keep"]),
        ("mmdd-xxxxxxx/Particle Info [PIC]", [], [".keep"]),
    ]
    with (
        patch("os.walk", return_value=mock_foldercontent),
        patch("logging.debug") as mock_debug,
    ):
        mmdd_xxxxxxx_folder_to_dict(Path("/path/to/dummy/"))
        assert mock_debug.call_count == 3


def test_mmdd_xxxxxxx_normal_behavior() -> None:
    """Test that data matches expectation."""
    mock_foldercontent = [
        ("mmdd-xxxxxxx", ["Particle Info [PIC]"], ["mock_array.txt"]),
        (
            "mmdd-xxxxxxx/Particle Info [PIC]",
            [],
            ["mock_int.txt", "mock_float.txt"],
        ),
    ]
    loadtxt_values = (
        np.array([[0.0, 1000], [1.0, 1200], [2.0, 1900]]),
        np.array(5),
        np.array(42.0),
    )
    expected = {
        "mock_array": np.array([[0.0, 1000], [1.0, 1200], [2.0, 1900]]),
        "mock_int": 5.0,
        "mock_float": 42.0,
    }
    with (
        patch("os.walk", return_value=mock_foldercontent),
        patch("numpy.loadtxt", side_effect=loadtxt_values),
    ):
        returned = mmdd_xxxxxxx_folder_to_dict(Path("dummy.txt"))
        assert returned.keys() == expected.keys()
        for key, value in returned.items():
            expected_val = expected[key]
            if not isinstance(value, np.ndarray):
                assert value == expected_val and type(value) == type(
                    expected_val
                )
                continue
            np.testing.assert_allclose(value, expected_val)
