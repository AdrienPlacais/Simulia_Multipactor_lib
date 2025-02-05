"""Define a base object to store a multipactor simulation results."""

import logging
from abc import ABC
from typing import Any, Callable, Literal

import numpy as np
import pandas as pd

from simultipac.plotter.default import DefaultPlotter
from simultipac.plotter.plotter import Plotter
from simultipac.util.exponential_growth import ExpGrowthParameters, fit_alpha

DATA_0D = Literal["id", "e_acc", "p_rms", "alpha"]
DATA_1D = Literal["time", "population", "modelled_population"]


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
        period: float | None = None,
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
        period : float | None, optional
            RF period in ns. Mandatory for exponential growth fits.

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
        self._exp_growth_parameters: ExpGrowthParameters | dict[str, float] = (
            {}
        )
        self._period: float | None = period
        self._modelled_population: np.ndarray | None = None

    def __str__(self) -> str:
        """Print minimal info on current simulation."""
        info = [f"Sim. #{self.id}", f"E_acc = {self.e_acc:.3e} V/m"]
        if len(self._exp_growth_parameters) == 0:
            return ", ".join(info)
        info.append(r"$\alpha = $" + f"{self.alpha} ns^-1")
        return ", ".join(info)

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
        alpha = self._exp_growth_parameters.get("alpha", None)
        if alpha is not None:
            return alpha
        logging.warning(
            "Exponential growth factor not calculated yet. Returnin NaN."
        )
        return np.nan

    def fit_alpha(
        self,
        fitting_periods: int,
        running_mean: bool = True,
        log_fit: bool = True,
        minimum_final_number_of_electrons: int = 0,
        bounds: tuple[list[float], list[float]] = (
            [1e-10, -10.0],
            [np.inf, 10.0],
        ),
        initial_values: list[float | None] = [None, -9.0],
        **kwargs,
    ) -> None:
        """Fit exp growth factor.

        Parameters
        ----------
        fitting_periods : int
            Number of periods over which the exp growth is searched. Longer is
            better, but you do not want to start the fit before the exp growth
            starts.
        running_mean : bool, optional
            To tell if you want to average the number of particles over one
            period. Highly recommended. The default is True.
        log_fit : bool, optional
            To perform the fit on :func:`exp_growth_log` rather than
            :func:`exp_growth`. The default is True, as it generally shows
            better convergence.
        minimum_final_number_of_electrons : int, optional
            Under this final number of electrons, we do no bother finding the
            exp growth factor and set all fit parameters to ``NaN``.
        bounds : tuple[list[float], list[float]], optional
            Upper bound and lower bound for the two variables: initial number
            of electrons, exp growth factor.
        initial_values: list[float | None], optional
            Initial values for the two variables: initial number of electrons,
            exp growth factor.

        """
        assert self._period is not None, "RF period is needed."
        fitting_range = self._period * fitting_periods

        self._exp_growth_parameters = fit_alpha(
            self.time,
            self.population,
            fitting_range=fitting_range,
            period=self._period,
            running_mean=running_mean,
            log_fit=log_fit,
            minimum_final_number_of_electrons=minimum_final_number_of_electrons,
            bounds=bounds,
            initial_values=initial_values,
            **kwargs,
        )

    @property
    def modelled_population(self) -> np.ndarray:
        """Define evolution of population, as modelled."""
        if self._modelled_population is not None:
            return self._modelled_population
        if self._exp_growth_parameters is None:
            raise ValueError(
                "Cannot model population evolution if fit not performed."
            )
        model = self._exp_growth_parameters["model"]
        assert isinstance(model, Callable)
        self._modelled_population = model(
            self.time, **self._exp_growth_parameters
        )
        assert isinstance(self._modelled_population, np.ndarray)
        return self._modelled_population

    def plot(
        self,
        x: DATA_0D | DATA_1D,
        y: DATA_0D | DATA_1D,
        plotter: Plotter | None = None,
        label: str | Literal["auto"] | None = None,
        grid: bool = True,
        axes: Any | None = None,
        **kwargs,
    ) -> Any:
        """Plot ``y`` vs ``x`` using ``plotter.plot()`` method.

        Plottable data is stored in :data:`DATA_0D` and :data:`DATA_1D`.

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
        self,
        plotter: Plotter = DefaultPlotter(),
        freq_ghz: float | None = None,
        *args,
        **kwargs,
    ) -> None:
        """Instantiate object.

        Parameters
        ----------
        plotter : Plotter, optional
            Object to create the plots.
        freq_ghz : float | None, optional
            RF frequency in GHz. Used to compute RF period, which is mandatory
            for exp growth fitting.

        """
        self._plotter = plotter
        self._freq_ghz = freq_ghz
        self._period = 1.0 / freq_ghz if freq_ghz is not None else None
