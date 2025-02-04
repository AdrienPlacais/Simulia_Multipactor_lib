"""Define a base object to store a multipactor simulation results."""

from abc import ABC
from typing import Any

import numpy as np

from simultipac.plotter.default import DefaultPlotter
from simultipac.plotter.plotter import Plotter


class ShapeMismatchError(Exception):
    """Raise error when ``population`` and ``time`` have different shapes."""


class SimulationResults(ABC):
    """Store a single simulation results."""

    def __init__(
        self,
        id: int,
        e_acc: float,
        p_rms: float | None,
        time: np.ndarray,
        population: np.ndarray,
        plotter: Plotter = DefaultPlotter(),
        trim_trailing: bool = False,
        **kwargs,
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
        plotter : Plotter, optional
            An object allowing to plot data.
        trim_trailing : bool, optional
            To remove the last simulation points, when the population is 0.
            Used with SPARK3D (``CSV`` import) for consistency with CST.

        """
        self.id = id
        self.e_acc = e_acc
        self.p_rms = p_rms
        self.time = time
        self.population = population
        self._plotter = plotter
        self._check_consistent_shapes()
        if trim_trailing:
            self._trim_trailing()

    def _check_consistent_shapes(self) -> None:
        """Raise an error if ``time`` and ``population`` have diff shapes."""
        if self.time.shape == self.population.shape:
            return
        raise ShapeMismatchError(
            f"{self.time.shape = } but {self.population.shape = }"
        )

    def _trim_trailing(self) -> None:
        """Remove data for which population is null."""
        idx_to_remove = np.argwhere(self.population == 0.0)
        if idx_to_remove.size == 0:
            return
        last_idx = idx_to_remove[0][0]
        self.population = self.population[:last_idx]
        self.time = self.time[:last_idx]

    def fit_alpha(
        self, fitting_periods: int, model: str = "classic", **kwargs
    ) -> None:
        """Fit exp growth factor."""
        raise NotImplementedError

    def plot(
        self,
        x: str,
        y: str,
        plotter: Plotter | None = None,
        axes: Any | None = None,
    ) -> Any:
        """Plot ``y`` vs ``x`` using ``plotter.plot()`` method.

        If ``axes`` is provided, add the plots on top of it. If ``idx_to_plot``
        is provided, plot only the corresponding :class:`.SimulationResults`.

        """
        if plotter is None:
            plotter = self._plotter
        raise NotImplementedError


class SimulationResultsFactory(ABC):
    """Easily create :class:`.SimulationResults`."""

    def __init__(
        self, plotter: Plotter = DefaultPlotter(), *args, **kwargs
    ) -> None:
        """Instantiate object."""
        self._plotter = plotter
