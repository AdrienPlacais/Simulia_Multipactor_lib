"""Define a set of simulation results."""

import bisect
from typing import Iterator

from simultipac.simulation_results.simulation_results import SimulationResults


class SimulationsResults:
    """Store multiple :class:`.SimulationResults` with retrieval methods."""

    def __init__(self) -> None:
        """Instantiate object."""
        self._results_by_id: dict[int, SimulationResults] = {}
        self._results_sorted_acc_field: list[SimulationResults] = []

    def add(self, result: SimulationResults) -> None:
        """Add a new :class:`SimulationResults` instance."""
        if result.id in self._results_by_id:
            raise ValueError(
                f"SimulationResult with id {result.id} already exists."
            )

        self._results_by_id[result.id] = result
        bisect.insort(
            self._results_sorted_acc_field, result, key=lambda r: r.acc_field
        )

    def get_by_id(self, result_id: int) -> SimulationResults | None:
        """Retrieve a :class:`SimulationResults` by its ID."""
        return self._results_by_id.get(result_id)

    def get_sorted_by_acc_field(self) -> list[SimulationResults]:
        """Retrieve all results sorted by ``acc_field``."""
        return self._results_sorted_acc_field

    def __iter__(self) -> Iterator[SimulationResults]:
        """Allow iteration over stored results."""
        return iter(self._results_sorted_acc_field)
