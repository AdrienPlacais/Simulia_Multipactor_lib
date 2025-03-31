"""Test the correct behavior of :class:`.CSTResults`."""

from unittest.mock import MagicMock

import numpy as np
import pytest

from simultipac.cst.simulation_results import CSTResults


@pytest.mark.implementation
def test_cst_results_initialization(mocker: MagicMock) -> None:
    """Test initialization of :class:`.CSTResults` object."""
    time = np.array([0, 1, 2, 3])
    population = np.array([10, 8, 5, 0])
    parameters = {"B_field": 1.2, "n_steps": 100}
    mocker.patch("is_file", return_value=True)
    result = CSTResults(
        id=1,
        e_acc=5.0,
        time=time,
        population=population,
        p_rms=2.0,
        parameters=parameters,
    )

    assert result.id == 1
    assert result.e_acc == 5.0
    assert result.p_rms == 2.0
    assert result.parameters == parameters
    assert np.array_equal(result.time, time)
    assert np.array_equal(result.population, population)
