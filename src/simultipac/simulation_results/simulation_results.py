"""Define a base object to store a multipactor simulation results."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from pathlib import Path

import numpy as np


class SimulationResults(ABC):
    """Store a single simulation results."""

    def __init__(
        self,
        id: int,
        e_acc: float,
        p_rms: float | None,
        time: np.ndarray,
        population: np.ndarray,
        trim_trailing: bool = False,
    ) -> None:
        """Instantiate, post-process.

        Parameters
        ----------
        id : int
            Unique simulation identifier.
        e_acc : float
            Accelerating field in V/m.
        p_rms : float | None
            RMS power in W.
        time : np.ndarray
            Time in ns.
        population : np.ndarray
            Evolution of population with time. Same shape as ``time``.
        trim_trailing : bool, optional
            To remove the last simulation points, when the population is 0.
            Used with SPARK3D (``CSV`` import) for consistency with CST.

        """
        self.id = id
        self.e_acc = e_acc
        self.p_rms = p_rms
        self.time = time
        self.population = population
        if trim_trailing:
            self._trim_trailing()

    def _trim_trailing(self) -> None:
        """Remove data for which population is null."""
        idx_to_remove = np.argwhere(self.population[:, 1] == 0.0)
        if idx_to_remove.size == 0:
            return
        last_idx = idx_to_remove[0][0]
        self.population = self.population[:last_idx]


class SimulationResultsFactory(ABC):
    """Easily create :class:`.SimulationResults`."""

    @abstractmethod
    def from_file(
        self, filepath: Path, e_acc: np.ndarray, delimiter: str = " ", **kwargs
    ) -> Sequence[SimulationResults]:
        """Load a file and create associate :class:`.SimulationResults`."""
