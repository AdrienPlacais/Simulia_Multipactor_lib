"""Define a base object to store a multipactor simulation results."""

import logging
from abc import ABC
from typing import Any, Literal

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
        self._alpha = None

    def __str__(self) -> str:
        """Print minimal info on current simulation."""
        return f"Sim. #{self.id}, E_acc = {self.e_acc:.3e} V/m"

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

    @property
    def alpha(self) -> float:
        """Return the exponential growth factor in 1/ns."""
        if self._alpha is not None:
            return self._alpha
        logging.warning(
            "Exponential growth factor not calculated yet. Returnin NaN."
        )
        return np.nan

    @alpha.setter
    def alpha(self, value: float) -> None:
        """Set the value of exponential growh factor in 1/ns."""
        self._alpha = value

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
        label: str | Literal["auto"] | None = None,
        grid: bool = True,
        axes: Any | None = None,
        **kwargs,
    ) -> Any:
        """Plot ``y`` vs ``x`` using ``plotter.plot()`` method.

        Parameters
        ----------
        x, y : str
            Name of properties to plot.
        plotter : Plotter | None, optional
            Object to use for plot. If not provided, we use ``self._plotter``.
        label : str | Literal["auto"] | None, optional
            If provided, overrides the legend. Useful when several simulations
            are shown on the same plot. Use the magic keyword ``"auto"`` to
            legend with a short description of current object.
        grid : bool, optional
            If grid should be plotted. Default is True.
        axes : Axes | NDArray[Any] | None, optional
            Axes to re-use, if provided. The default is None (plot on new
            axis).
        kwargs :
            Other keyword arguments passed to the :meth:`.Plotter.plot` method.

        Returns
        -------
        Any
            Objects created by the :meth:`.Plotter.plot`.

        """
        if plotter is None:
            plotter = self._plotter
        data = self._to_pandas(x, y)

        if label == "auto":
            label = str(self)

        axes = plotter.plot(
            data, x=x, y=y, grid=grid, axes=axes, label=label, **kwargs
        )
        return axes

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
