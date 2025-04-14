"""Define a set of simulation results."""

import bisect
import logging
from collections.abc import Collection, Generator, Iterable, Sequence
from functools import reduce
from itertools import product
from pathlib import Path
from typing import Any, Iterator, Literal

import numpy as np
import pandas as pd

from simultipac.cst.simulation_results import CSTResultsFactory
from simultipac.plotter.default import DefaultPlotter
from simultipac.plotter.plotter import Plotter
from simultipac.simulation_results.simulation_results import SimulationResults
from simultipac.spark3d.simulation_results import Spark3DResultsFactory
from simultipac.types import DATA_0D, DATA_0D_t, DATA_1D_t


class UnsupportedToolError(Exception):
    """Raise for simulation tool different from SPARK3D or CST."""


class DuplicateIndexError(Exception):
    """Raise for simulation ID already existing."""


class NonExistingIDError(Exception):
    """Raise when asking a non-existent ID."""


class SimulationsResults:
    """Store multiple :class:`.SimulationResults` with retrieval methods.

    :class:`.SimulationResult` are stored in ``self`` in the order they are
    given.

    """

    def __init__(
        self,
        simulations_results: Iterable[SimulationResults],
        plotter: Plotter | None = None,
    ) -> None:
        """Sort and store the given :class:`.SimulationResults` instances.

        Parameters
        ----------
        simulations_results :
            The individual results instances.
        plotter :
            An object to create the plots.

        """
        self._results_by_id: dict[int, SimulationResults] = {}

        #: :class:`.SimulationResults` sorted by increasing accelerating field
        self._results: list[SimulationResults] = []
        for x in simulations_results:
            self._add(x)

        if plotter is None:
            plotter = DefaultPlotter()
        self._plotter = plotter
        self._color: Any = None

    def __iter__(self) -> Iterator[SimulationResults]:
        """Allow iteration over stored results."""
        return iter(self._results)

    def __len__(self) -> int:
        """Return number of elements."""
        return len(self._results)

    def _add(self, result: SimulationResults) -> None:
        """Add a new :class:`SimulationResults` instance."""
        if result.id in self._results_by_id:
            raise DuplicateIndexError(
                f"SimulationResult with id {result.id} already exists."
            )

        self._results_by_id[result.id] = result
        bisect.insort(self._results, result, key=lambda r: r.e_acc)

    def get_by_id(self, result_id: int) -> SimulationResults:
        """Retrieve a :class:`SimulationResults` by its ID."""
        result = self._results_by_id.get(result_id)
        if result is not None:
            return result
        raise NonExistingIDError(f"No simulation results with ID {result_id}")

    @property
    def to_list(self) -> list[SimulationResults]:
        """Retrieve all results sorted by ``acc_field``."""
        return self._results

    def plot(
        self,
        x: DATA_0D_t | DATA_1D_t,
        y: DATA_0D_t | DATA_1D_t,
        idx_to_plot: Iterable[int] | None = None,
        id_to_plot: Iterable[int] | None = None,
        to_plot: Iterable[SimulationResults] | None = None,
        plotter: Plotter | None = None,
        label: str | Literal["auto"] | None = "auto",
        grid: bool = True,
        axes: Any | None = None,
        sort_by_parameter: Collection[str] | None = None,
        **kwargs,
    ) -> Any:
        """Recursively call :meth:`.SimulationResults.plot`.

        .. note::
            0D ``x`` vs ``y`` not implemented yet.

        Parameters
        ----------
        x, y :
            Name of properties to plot.
        idx_to_plot :
            Positions in the list of :class:`.SimulationResults` sorted by
            growing accelerating field / power. Not considered if
            ``id_to_plot`` or ``to_plot`` is provided.
        id_to_plot :
            ID attributes; takes preceedence over ``idx_to_plot``. Not
            considered if ``to_plot`` is provided.
        to_plot :
            Objects to plot; takes preceedence over ``idx_to_plot`` and
            ``id_to_plot``.
        plotter :
            Object to use for plot. If not provided, we use :attr:`._plotter`.
        label :
            If provided, overrides the legend. Useful when several simulations
            are shown on the same plot. Use the magic keyword ``"auto"`` to
            legend with a short description of current object.
        grid :
            If grid should be plotted. Default is True.
        axes :
            Axes to re-use, if provided.
        sort_by_parameter :
            If provided, results are grouped by the given parameters before
            plotting.
        kwargs :
            Other keyword arguments passed to the :meth:`.Plotter.plot` method.

        Returns
        -------
        Any
            Objects created by the :meth:`.Plotter.plot`.

        """
        if plotter is None:
            plotter = self._plotter

        if sort_by_parameter is not None:
            parameters_values = self.parameter_values(*sort_by_parameter)
            for param_combination in product(
                *[parameters_values[p] for p in sort_by_parameter]
            ):
                filters = dict(zip(sort_by_parameter, param_combination))
                to_plot = self.with_parameter_value(filters)
                label = ", ".join(f"{p}={v}" for p, v in filters.items())
                axes = self.plot(
                    x=x,
                    y=y,
                    plotter=plotter,
                    label=label,
                    grid=grid,
                    axes=axes,
                    to_plot=to_plot,
                    sort_by_parameter=None,
                    color=None,
                    **kwargs,
                )
            return axes

        to_plot = self._to_plot(idx_to_plot, id_to_plot, to_plot)

        if x in DATA_0D and y in DATA_0D:
            return self._plot_0d(
                x=x,
                y=y,
                plotter=plotter,
                label=label,
                grid=grid,
                axes=axes,
                to_plot=to_plot,
                **kwargs,
            )

        for result in to_plot:
            axes = result.plot(
                x=x,
                y=y,
                plotter=plotter,
                label=label,
                grid=grid,
                axes=axes,
                **kwargs,
            )
        return axes

    def _to_plot(
        self,
        idx_to_plot: Iterable[int] | None = None,
        id_to_plot: Iterable[int] | None = None,
        to_plot: Iterable[SimulationResults] | None = None,
    ) -> list[SimulationResults]:
        """Give the :class:`.SimulationResults` to plot.

        When all arguments are ``None``, we return all the stored
        :class:`.SimulationResults`.

        Parameters
        ----------
        idx_to_plot :
            Positions in the list of :class:`.SimulationResults` sorted by
            growing accelerating field / power. Not considered if
            ``id_to_plot`` or ``to_plot`` is provided.
        id_to_plot :
            ID attributes; takes preceedence over ``idx_to_plot``. Not
            considered if ``to_plot`` is provided.
        to_plot :
            Objects to plot; takes preceedence over ``idx_to_plot`` and
            ``id_to_plot``.

        """
        if to_plot is not None:
            return [r for r in to_plot]
        if id_to_plot is not None:
            return [self.get_by_id(id) for id in id_to_plot]
        if idx_to_plot is None:
            idx_to_plot = range(len(self))
        return [self._results[idx] for idx in idx_to_plot]

    def _plot_0d(
        self,
        x: DATA_0D_t,
        y: DATA_0D_t,
        plotter: Plotter,
        label: str | Literal["auto"] | None = None,
        grid: bool = True,
        axes: Any | None = None,
        to_plot: Sequence[SimulationResults] | None = None,
        color: Any = "auto",
        **kwargs,
    ) -> Any:
        """Concatenate and plot 0D data from ``results``.

        Parameters
        ----------
        x, y :
            Name of properties to plot.
        plotter :
            Object to use for plot.
        label :
            If provided, overrides the legend. Useful when several simulations
            are shown on the same plot. Use the magic keyword ``"auto"`` to
            legend with a short description of current object.
        grid :
            If grid should be plotted. Default is True.
        axes :
            Axes to re-use, if provided.
        to_plot :
            The objects to plot. If not given, plot all the objects.
        color :
            Color for the plot. If "auto", we use the
            :attr:`.SimulationsResults._color` attribute.
        kwargs :
            Other keyword arguments passed to the :meth:`.Plotter.plot` method.

        Returns
        -------
        Any
            Objects created by the :meth:`.Plotter.plot`.

        """
        data = self._to_pandas(x, y, results=to_plot)

        if label == "auto":
            n_simulations = f"{len(self)} simulations"
            if to_plot is not None:
                n_simulations = f"{len(to_plot)} simulations"
            label = f"SimulationsResults ({n_simulations})"

        axes, color = plotter.plot(
            data,
            x=x,
            y=y,
            grid=grid,
            axes=axes,
            label=label,
            color=self._color if color == "auto" else color,
            **kwargs,
        )
        if self._color is None:
            self._color = color
        return axes

    def _to_pandas(
        self,
        *args: DATA_0D_t,
        results: Sequence[SimulationResults] | None = None,
    ) -> pd.DataFrame:
        """Concatenate all attributes which name is in ``args`` to a dataframe.

        .. todo::
            Review this and its error handling

        Parameters
        ----------
        args :
            Name of :class:`.SimulationResults` arguments to concatenate.
        results :
            If given, we concatenate only the data frome these
            :class:`.SimulationResults`.

        Returns
        -------
        pandas.DataFrame
            Holds the values of every element of ``args``.

        Raises
        ------
        ValueError:
            If one of the ``args`` is an array or is missing.

        """
        if results is None:
            results = self.to_list

        data: dict[str, list[float]] = {}

        for arg in args:
            concat: list[float] = []
            for result in results:
                value = getattr(result, arg, None)
                if not isinstance(value, (float, int)):
                    logging.debug(
                        f"The {arg} attribute of {result} is not a float but a"
                        f" {type(value)}, so it was not added to the "
                        "dataframe."
                    )
                    continue
                concat.append(value)
            data[arg] = concat

        lengths = {key: len(value) for key, value in data.items()}
        if len(set(lengths.values())) > 1:
            raise ValueError(
                "All the lists in data must have the same length. Maybe "
                f"{results = } is a Generator? Or maybe one of the keys was "
                "not found in one or more of the SimulationResults?\n"
                f"{lengths = }"
            )

        try:
            return pd.DataFrame(data)
        except ValueError as e:
            raise ValueError(
                f"Could not get a data, creating malformed dataframe.\n{e}"
            )

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
        fitting_periods :
            Number of periods over which the exp growth is searched. Longer is
            better, but you do not want to start the fit before the exp growth
            starts.
        running_mean :
            To tell if you want to average the number of particles over one
            period. Highly recommended.
        log_fit :
            To perform the fit on :func:`exp_growth_log` rather than
            :func:`exp_growth`. The default is True, as it generally shows
            better convergence.
        minimum_final_number_of_electrons :
            Under this final number of electrons, we do no bother finding the
            exp growth factor and set all fit parameters to ``NaN``.
        bounds :
            Upper bound and lower bound for the two variables: initial number
            of electrons, exp growth factor.
        initial_values: list[float], optional
            Initial values for the two variables: initial number of electrons,
            exp growth factor.

        """
        for result in self:
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
        *to_save: DATA_0D_t | DATA_1D_t,
        sep: str = ",",
        merge_on: DATA_0D_t | DATA_1D_t | None = None,
        **kwargs,
    ) -> None:
        """Concatenate all data named ``to_save`` and save it to a file.

        Parameters
        ----------
        filepath :
            Where to save the file.
        to_save :
            The list of quantities to save.
        sep :
            Column separator. Default is a comma.
        merge_on :
            If provided, the different dataframe will be merged against this
            column. Typical usage is ``merge_on="time"`` to have a single time
            column.

        """
        if isinstance(filepath, str):
            filepath = Path(filepath)

        df = self._format_for_save(*to_save, merge_on=merge_on, **kwargs)

        df.to_csv(filepath, sep=sep, **kwargs)
        logging.info(f"File saved to {filepath.absolute()}")
        return

    def _format_for_save(
        self,
        *to_save: DATA_0D_t | DATA_1D_t,
        merge_on: DATA_0D_t | DATA_1D_t | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Concatanate desired data into a single dataframe.

        Parameters
        ----------
        to_save :
            The list of quantities to save.
        merge_on :
            If provided, the different dataframe will be merged against this
            column. Typical usage is ``merge_on="time"`` to have a single time
            column.

        Returns
        -------
        pd.DataFrame
            Contains all the data to save, with proper format.

        """
        if all(arg in DATA_0D for arg in to_save):
            return self._to_pandas(*to_save, **kwargs)  # type: ignore

        all_df = [x.to_pandas(*to_save, **kwargs) for x in self.to_list]

        if merge_on is None:
            return pd.concat(all_df, axis=1)

        assert merge_on in to_save, (
            f"Cannot merge dataframes on column {merge_on} because it does not"
            f" exist. Please add it to {to_save = }"
        )
        renamed_dfs = []
        for df, res in zip(all_df, self.to_list):
            new_cols = {
                col: f"{col}_{res.id}" for col in to_save if col != merge_on
            }
            renamed_dfs.append(df.rename(columns=new_cols))
        merged_df = reduce(
            lambda left, right: left.merge(right, on=merge_on), renamed_dfs
        )
        return merged_df

    def parameter_values(
        self,
        *parameters: str,
        default: Any = None,
        allow_missing: bool = False,
    ) -> dict[str, set]:
        """Get the existing values of all ``parameters`` in the stored results.

        If no parameters are given, return all parameters with their possible
        values.

        Parameters
        ----------
        *parameters :
            Name of the parameter(s) to get. Must be key in the ``parameters``
            dictionary of the stored :class:`.SimulationResult`. If empty, all
            parameters found in any result are returned.
        default :
            The fallback value when the ``parameter`` is not a key of a
            :attr:`.SimulationResult.parameters`.
        allow_missing :
            If True, an error is raised when ``default`` is present in the
            output set.

        Returns
        -------
        all_values : dict[str, set]
            Keys are all the ``parameters``. Values corresponding values in
            every storred :class:`.SimulationResult`.

        """
        all_values = {}

        if not parameters:
            parameters = tuple(
                {key for result in self.to_list for key in result.parameters}
            )
        for parameter in parameters:
            values = set()
            missing_results = []

            for result in self.to_list:
                value = result.parameters.get(parameter, default)
                values.add(value)
                if value is default:
                    missing_results.append(result)

            all_values[parameter] = values
            if not missing_results:
                continue

            logging.debug(
                f"Missing {parameter} in {len(missing_results)} results"
            )
            if not allow_missing:
                raise ValueError(
                    f"Missing {parameter} in the following SimulationResults:"
                    f"\n{missing_results}"
                )

        return all_values

    def with_parameter_value(
        self, parameters: dict[str, Any]
    ) -> Generator[SimulationResults, None, None]:
        """Yield :class:`.SimulationResults` matching given parameter values.

        Parameters
        ----------
        parameters :
            Parameter names and their required values.

        Yields
        ------
        SimulationResults
            :class:`.SimulationResults` instances whose parameters match the
            given values.

        """
        for result in self.to_list:
            if all(
                result.parameters.get(param) == value
                for param, value in parameters.items()
            ):
                yield result

    def show(self) -> None:
        """Show the plots that were produced.

        Useful for the bash interface.

        """
        return self._plotter.show()


class SimulationsResultsFactory:
    """An object to create a :class:`.SimulationsResults`."""

    def __init__(
        self,
        tool: Literal["SPARK3D", "CST"],
        plotter: Plotter | None = None,
        freq_ghz: float | None = None,
        *args,
        **kwargs,
    ) -> None:
        """Create object to easily generate simulation results.

        Parameters
        ----------
        tool: str
            Name of the tool.
        plotter :
            Object to create the plots.
        freq_ghz :
            RF frequency in GHz. Used to compute RF period, which is mandatory
            for exp growth fitting.

        """
        if plotter is None:
            plotter = DefaultPlotter()
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
        plotter :
            An object to plot data.
        filepath :
            Filepath to a ``TXT`` or ``CSV`` file for SPARK3D.
        master_folder :
            Filepath to the folder holding all the ``mmdd-xxxxxxx`` folders for
            CST.
        e_acc :
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
        plotter :
            An object to plot data.
        filepath :
            Filepath to a ``TXT`` or ``CSV`` file for SPARK3D.
        master_folder :
            Filepath to the folder holding all the ``mmdd-xxxxxxx`` folders for
            CST.
        e_acc :
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
