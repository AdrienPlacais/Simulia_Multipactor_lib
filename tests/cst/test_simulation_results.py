"""Test the correct behavior of :class:`.CSTResults`."""

import numpy as np

from simultipac.cst.simulation_results import CSTResults


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
