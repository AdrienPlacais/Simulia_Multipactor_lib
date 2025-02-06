"""Define tests for :class:`.SimulationsResults`."""

from unittest.mock import MagicMock

import numpy as np
import pytest

from simultipac.simulation_results.simulation_results import SimulationResults
from simultipac.simulation_results.simulations_results import (
    DuplicateIndexError,
    SimulationsResults,
)


def test_add(mocker: MagicMock) -> None:
    """Test :meth:`.SimulationsResults._add`."""
    time = np.linspace(0, 10, 11)
    pop = time
    n_results = 5

    results = (
        SimulationResults(id=i, e_acc=i, time=time, population=pop)
        for i in range(n_results)
    )
    mock_add = mocker.patch.object(SimulationsResults, "_add")
    SimulationsResults(results)
    assert mock_add.call_count == n_results


def test_add_double_id_error() -> None:
    """Test :meth:`.SimulationsResults._add`."""
    time = np.linspace(0, 10, 11)
    population = time
    n_results = 5

    results = (
        SimulationResults(
            id=i if i > 0 else 1, e_acc=i, time=time, population=population
        )
        for i in range(n_results)
    )
    with pytest.raises(DuplicateIndexError):
        SimulationsResults(results)


def test_len() -> None:
    """Test :meth:`.SimulationsResults._add`."""
    time = np.linspace(0, 10, 11)
    pop = time
    n_results = 5

    results = (
        SimulationResults(id=i, e_acc=i, time=time, population=pop)
        for i in range(n_results)
    )

    assert len(SimulationsResults(results)) == n_results


def test_e_acc_sorting() -> None:
    """Check that results are sorted by increasing ``e_acc``."""
    time = np.linspace(0, 10, 11)
    pop = time
    unsorted_results = (
        r3 := SimulationResults(id=3, e_acc=3, time=time, population=pop),
        r1 := SimulationResults(id=1, e_acc=1, time=time, population=pop),
        r0 := SimulationResults(id=0, e_acc=0, time=time, population=pop),
        r4 := SimulationResults(id=4, e_acc=4, time=time, population=pop),
        r2 := SimulationResults(id=2, e_acc=2, time=time, population=pop),
    )
    simulations_results = SimulationsResults(unsorted_results)

    expected = [r0, r1, r2, r3, r4]
    assert simulations_results.to_list == expected


def test_get_by_id() -> None:
    """Test :meth:`.SimulationsResults._get_by_id`."""
    time = np.linspace(0, 10, 11)
    pop = time
    unsorted_results = (
        r3 := SimulationResults(id=3, e_acc=3, time=time, population=pop),
        r1 := SimulationResults(id=1, e_acc=1, time=time, population=pop),
        r0 := SimulationResults(id=0, e_acc=0, time=time, population=pop),
        r4 := SimulationResults(id=4, e_acc=4, time=time, population=pop),
        r2 := SimulationResults(id=2, e_acc=2, time=time, population=pop),
    )
    simulations_results = SimulationsResults(unsorted_results)
    assert simulations_results.get_by_id(3) is r3


def test_get_by_id_missing() -> None:
    """Test :meth:`.SimulationsResults._get_by_id`."""
    time = np.linspace(0, 10, 11)
    pop = time
    results = (
        SimulationResults(id=i, e_acc=i, time=time, population=pop)
        for i in range(5)
    )
    simulations_results = SimulationsResults(results)
    assert simulations_results.get_by_id(6) is None
