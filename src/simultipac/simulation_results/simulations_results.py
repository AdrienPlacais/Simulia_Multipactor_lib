"""Define a set of simulation results."""

import bisect
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any, Iterator, Literal

import numpy as np

from simultipac.cst.simulation_results import CSTResultsFactory
from simultipac.plotter.default import DefaultPlotter
from simultipac.plotter.plotter import Plotter
from simultipac.simulation_results.simulation_results import (
    DATA_0D,
    DATA_1D,
    SimulationResults,
)
from simultipac.spark3d.simulation_results import Spark3DResultsFactory


class UnsupportedToolError(Exception):
    """Raise for simulation tool different from SPARK3D or CST."""


class SimulationsResults:
    """Store multiple :class:`.SimulationResults` with retrieval methods."""

    def __init__(
        self,
        simulations_results: Iterable[SimulationResults],
        plotter: Plotter,
    ) -> None:
        """Instantiate object."""
        self._results_by_id: dict[int, SimulationResults] = {}
        self._results_sorted_acc_field: list[SimulationResults] = []
        # Should populate other dictionaries too
        self._results = [x for x in simulations_results]
        self._plotter = plotter

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

    def plot(
        self,
        x: DATA_0D | DATA_1D,
        y: DATA_0D | DATA_1D,
        idx_to_plot: Iterable[int] | None = None,
        plotter: Plotter | None = None,
        label: str | Literal["auto"] | None = "auto",
        grid: bool = True,
        axes: Any | None = None,
        **kwargs,
    ) -> Any:
        """Recursively call :meth:`.SimulationResults.plot`.

        Plottable data is stored in :data:`.DATA_0D` and :data:`.DATA_1D`.

        Parameters
        ----------
        x, y : str
            Name of properties to plot.
        idx_to_plot : Iterable[int] | None, optional
            If provided, plot only the :class:`.SimulationResult` with those
            ids.
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
        if idx_to_plot is None:
            idx_to_plot = (results.id for results in self._results)

        for idx in idx_to_plot:
            axes = self._results[idx].plot(
                x=x,
                y=y,
                plotter=plotter,
                label=label,
                grid=grid,
                axes=axes,
                **kwargs,
            )
        return axes

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
        initial_values: list[float] = [0.0, 0.0],
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
        initial_values: list[float], optional
            Initial values for the two variables: initial number of electrons,
            exp growth factor.

        """
        for result in self._results:
            result.fit_alpha(
                fitting_periods=fitting_periods,
                running_mean=running_mean,
                log_fit=log_fit,
                minimum_final_number_of_electrons=minimum_final_number_of_electrons,
                bounds=bounds,
                initial_values=initial_values,
                **kwargs,
            )

    def save(
        self,
        filepath: Path | str,
        *to_save: str,
        delimiter: str = "\t",
        **kwargs,
    ) -> None:
        """Concatenate all data named ``to_save`` and save it to a file."""
        raise NotImplementedError


class SimulationsResultsFactory:
    """An object to create a :class:`.SimulationsResults`."""

    def __init__(
        self,
        tool: Literal["SPARK3D", "CST"],
        plotter: Plotter = DefaultPlotter(),
        freq_ghz: float | None = None,
        *args,
        **kwargs,
    ) -> None:
        """Create object to easily generate simulation results.

        Parameters
        ----------
        tool: str
            Name of the tool.
        plotter : Plotter, optional
            Object to create the plots.
        freq_ghz : float | None, optional
            RF frequency in GHz. Used to compute RF period, which is mandatory
            for exp growth fitting.

        """
        self._tool = tool
        self._plotter = plotter
        self._freq_ghz = freq_ghz

    def create(
        self,
        *,
        filepath: Path | None = None,
        master_folder: Path | None = None,
        e_acc: np.ndarray | None = None,
        **kwargs,
    ) -> SimulationsResults:
        """Create all the objects.

        Parameters
        ----------
        plotter : Plotter
            An object to plot data.
        filepath : Path | None
            Filepath to a ``TXT`` or ``CSV`` file for SPARK3D.
        master_folder : Path | None
            Filepath to the folder holding all the ``mmdd-xxxxxxx`` folders for
            CST.
        e_acc : np.ndarray | None
            The accelerating fields, used by SPARK3D.
        kwargs :
            Keyword arguments passed to the appropriate subclass of
            :class:`.SimulationResultsFactory`.

        Returns
        -------
        SimulationsResults
            A concatenation of the individual simulations.

        """
        individual_simulation_results = self._create_individual(
            filepath=filepath,
            master_folder=master_folder,
            e_acc=e_acc,
            plotter=self._plotter,
            **kwargs,
        )
        simulations_results = SimulationsResults(
            individual_simulation_results,
            plotter=self._plotter,
        )
        return simulations_results

    def _create_individual(
        self,
        *,
        plotter: Plotter,
        filepath: Path | None = None,
        master_folder: Path | None = None,
        e_acc: np.ndarray | None = None,
        **kwargs,
    ) -> Sequence[SimulationResults]:
        """Create several individual :class:`.SimulationResults`.

        Parameters
        ----------
        plotter : Plotter
            An object to plot data.
        filepath : Path | None
            Filepath to a ``TXT`` or ``CSV`` file for SPARK3D.
        master_folder : Path | None
            Filepath to the folder holding all the ``mmdd-xxxxxxx`` folders for
            CST.
        e_acc : np.ndarray | None
            The accelerating fields, used by SPARK3D.
        kwargs :
            Keyword arguments passed to the appropriate subclass of
            :class:`.SimulationResultsFactory`.

        Returns
        -------
        Sequence[SimulationResults]
            The individual :class:`.SimulationResults`.

        Raises
        ------
        NotImplementedError:
            When ``self._tool`` is not in ``("CST", "SPARK3D")``.

        """
        if self._tool == "CST":
            assert (
                master_folder is not None
            ), "You must provide the path to the CST mmdd-xxxxxxx folders"
            assert master_folder.is_dir(), f"{master_folder = } must exist"
            factory = CSTResultsFactory(
                plotter=plotter, freq_ghz=self._freq_ghz, **kwargs
            )
            return factory.from_simulation_folders(master_folder=master_folder)

        if self._tool == "SPARK3D":
            assert (
                filepath is not None
            ), "You must provide the path to the SPARK3D file results."
            assert filepath.is_file(), f"{filepath = } must exist"
            assert isinstance(e_acc, np.ndarray), (
                "You must provide an array of accelerating fields. You gave "
                f"{e_acc = }"
            )
            factory = Spark3DResultsFactory(
                plotter=plotter, freq_ghz=self._freq_ghz, **kwargs
            )
            return factory.from_file(filepath, e_acc=e_acc)
        raise NotImplementedError(f"The tool {self._tool} is not implemented.")
