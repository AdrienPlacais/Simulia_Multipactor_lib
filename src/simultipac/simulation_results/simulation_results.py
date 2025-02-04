"""Define a base object to store a multipactor simulation results."""

from abc import ABC
from typing import Any

import numpy as np
import pandas as pd

from simultipac.plotter.default import DefaultPlotter
from simultipac.plotter.plotter import Plotter


class ShapeMismatchError(Exception):
    """Raise error when ``population`` and ``time`` have different shapes."""


class MissingDataError(Exception):
    """Error raised when trying to access non-existing data."""


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

    def _to_pandas(self, *args: str) -> pd.DataFrame:
        """Concatenate all attribute arrays which name is in ``args`` to a df.

        Parameters
        ----------
        args : str
            Name of arguments as saved in current objects. Example:
                ``"population"``, ``"time"``...

        Returns
        -------
        pd.DataFrame
            Concatenates all desired data.

        Raises
        ------
        MissingDataError:
            If a string in ``args`` does not correspond to any attribute in
            ``self`` (or if corresponding value is ``None``).
        ValueError:
            If all the ``args`` are a single value (float/int/bool).

        """
        data: dict[str, float | np.ndarray] = {
            arg: value
            for arg in args
            if (value := getattr(self, arg, None)) is not None
        }
        if len(data) == len(args):
            try:
                return pd.DataFrame(data)
            except ValueError as e:
                raise ValueError(
                    "Foats/ints/bools are not gettable with this method if "
                    f"no array is asked at the same time.\n{e}"
                )

        missing = [arg for arg in args if getattr(self, arg, None) is None]
        raise MissingDataError(f"{missing} not found in {self}")


class SimulationResultsFactory(ABC):
    """Easily create :class:`.SimulationResults`."""

    def __init__(
        self, plotter: Plotter = DefaultPlotter(), *args, **kwargs
    ) -> None:
        """Instantiate object."""
        self._plotter = plotter
