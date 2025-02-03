"""Define a set of simulation results."""

import bisect
from pathlib import Path
from typing import Iterator, Literal, Self

from simultipac.cst.simulation_results import CSTResultsFactory
from simultipac.simulation_results.simulation_results import (
    SimulationResults,
    SimulationResultsFactory,
)
from simultipac.spark3d.simulation_results import Spark3DResultsFactory


class UnsupportedToolError(Exception):
    """Raise for simulation tool different from SPARK3D or CST."""


class SimulationsResults:
    """Store multiple :class:`.SimulationResults` with retrieval methods."""

    def __init__(self) -> None:
        """Instantiate object."""
        self._results_by_id: dict[int, SimulationResults] = {}
        self._results_sorted_acc_field: list[SimulationResults] = []

    @classmethod
    def from_folder(
        cls, folder: Path, tool: Literal["CST", "SPARK3D"]
    ) -> Self:
        """Load all files in the given folder."""
        paths = folder.glob("**/*")
        files = (x for x in paths if x.is_file())
        raise NotImplementedError

    def _results_factory(
        self, tool: Literal["CST", "SPARK3D"], **kwargs
    ) -> SimulationResultsFactory:
        """Get the proper results factory."""
        if tool == "SPARK3D":
            return Spark3DResultsFactory(**kwargs)
        if tool == "CST":
            return CSTResultsFactory(**kwargs)
        raise UnsupportedToolError

    def add(self, result: SimulationResults) -> None:
        """Add a new :class:`SimulationResults` instance."""
        if result.id in self._results_by_id:
            raise ValueError(
                f"SimulationResult with id {result.id} already exists."
            )

        self._results_by_id[result.id] = result
        bisect.insort(
            self._results_sorted_acc_field, result, key=lambda r: r.e_acc
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
