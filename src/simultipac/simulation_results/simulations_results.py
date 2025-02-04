"""Define a set of simulation results."""

import bisect
from collections.abc import Collection, Iterable, Sequence
from pathlib import Path
from typing import Any, Iterator, Literal

import numpy as np

from simultipac.cst.simulation_results import CSTResultsFactory
from simultipac.plotter.default import DefaultPlotter
from simultipac.plotter.plotter import Plotter
from simultipac.simulation_results.simulation_results import SimulationResults
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
        x: str,
        y: str,
        idx_to_plot: Iterable[int] | None = None,
        plotter: Plotter | None = None,
        axes: Any | None = None,
        autolabel: bool = True,
        **kwargs,
    ) -> Any:
        """Plot ``y`` vs ``x`` using ``plotter.plot()`` method.

        If ``axes`` is provided, add the plots on top of it. If ``idx_to_plot``
        is provided, plot only the corresponding :class:`.SimulationResults`.

        """
        if plotter is None:
            plotter = self._plotter
        if idx_to_plot is None:
            idx_to_plot = (results.id for results in self._results)
        axes = None
        for idx in idx_to_plot:
            axes = self._results[idx].plot(
                x=x, y=y, axes=axes, autolabel=autolabel, **kwargs
            )
        return axes

    def fit_alpha(
        self, fitting_periods: int, model: str = "classic", **kwargs
    ) -> None:
        """Fit exp growth factor of every :class:`.SimulationResults`."""
        for results in self._results:
            results.fit_alpha(
                fitting_periods=fitting_periods, model=model, **kwargs
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
        *args,
        **kwargs,
    ) -> None:
        """Create the object."""
        self._tool = tool
        self._plotter = plotter

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
            factory = CSTResultsFactory(plotter=plotter, **kwargs)
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
            factory = Spark3DResultsFactory(plotter=plotter, **kwargs)
            return factory.from_file(filepath, e_acc=e_acc)
        raise NotImplementedError(f"The tool {self._tool} is not implemented.")
