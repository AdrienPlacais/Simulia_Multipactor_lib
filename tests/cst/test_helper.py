"""Test the helper functions from the CST module."""

from pathlib import Path

import pytest

from simultipac.cst.helper import get_id, mmdd_xxxxxxx_folder_to_dict


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
