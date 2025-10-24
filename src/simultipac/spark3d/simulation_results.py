"""Define an object to store SPARK3D simulation results."""

from pathlib import Path

import numpy as np

from simultipac.plotter.plotter import Plotter
from simultipac.simulation_results.simulation_results import (
    SimulationResults,
    SimulationResultsFactory,
)


class Spark3DResults(SimulationResults):
    """Store a single SPARK3D simulation results."""

    def fit_alpha(
        self,
        fitting_periods: int,
        running_mean: bool = False,
        log_fit: bool = True,
        minimum_final_number_of_electrons: int = 0,
        bounds: tuple[list[float], list[float]] = (
            [1e-10, -10.0],
            [np.inf, 10.0],
        ),
        initial_values: list[float] = [0.0, 0.0],
        minimum_number_of_points: int = 4,
        min_points_per_period: int = 2,
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
            period. It is recommended with CST, but does not bring anything for
            SPARK3D. The default is False.
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
        minimum_number_of_points :
            Minimum number of fitting points; under this limit, a warning is
            issued. For CST, should be at least 10 or 20. With SPARK3D, there
            are two points per RF period so a value of 2 or 4 should be enough.
        min_points_per_period :
            Minimum number of points per period. In SPARK3D, we only have two
            points per RF period so this number should be lower to avoid
            unnecessary warnings.

        """
        return super().fit_alpha(
            fitting_periods=fitting_periods,
            running_mean=running_mean,
            log_fit=log_fit,
            minimum_final_number_of_electrons=minimum_final_number_of_electrons,
            bounds=bounds,
            initial_values=initial_values,
            minimum_number_of_points=minimum_number_of_points,
            min_points_per_period=min_points_per_period,
            **kwargs,
        )


class Spark3DResultsFactory(SimulationResultsFactory):
    """Define an object to easily instantiate :class:`.Spark3DResults`."""

    def __init__(
        self,
        plotter: Plotter | None = None,
        freq_ghz: float | None = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(plotter=plotter, freq_ghz=freq_ghz, *args, **kwargs)

    def from_file(
        self,
        filepath: Path,
        e_acc: np.ndarray,
        delimiter: str | None = None,
        **kwargs,
    ) -> list[Spark3DResults]:
        """Load a ``TXT`` or ``CSV`` file and create associated objects.

        Parameters
        ----------
        filepath :
            Filepath to a ``TXT`` or ``CSV`` SPARK3D file. See
            :meth:`Spark3DResultsFactory._from_csv` and
            :meth:`Spark3DResultsFactory._from_txt` for information on how to
            create/where to find these files.
        e_acc :
            The accelerating fields in :unit:`V/m`.
        delimiter :
            Column separator.

        """
        filetype = filepath.suffix
        if filetype == ".txt":
            return self._from_txt(
                filepath=filepath, e_acc=e_acc, delimiter=delimiter, **kwargs
            )
        if filetype == ".csv":
            return self._from_csv(
                filepath=filepath, e_acc=e_acc, delimiter=delimiter, **kwargs
            )
        raise OSError(f"SPARK3D files must be CSV or TXT. I got {filetype = }")

    def _from_txt(
        self,
        filepath: Path,
        e_acc: np.ndarray,
        delimiter: str | None = "\t",
        **kwargs,
    ) -> list[Spark3DResults]:
        """
        Create several :class:`.Spark3DResults` from :file:`time_results.txt`.

        This file is generally produced with SPARK3D CLI. ``TXT`` file looks
        like this::

        #Sim num	Power(W)	Time(s)	Num.elec.
        1	100	0	1000
        1	100	1	1010
        1	100	2	1020
        ...	...	...	...
        2	50	0	1000
        2	50	1	900
        2	50	2	500
        ...	...	...	...

        It is typically stored in ``<project_name>/Results/@Mod1/@ConfGr1/
        @EMConfGr1/@MuConf1/region1/signalCW 1/``.

        .. todo::
            Handle malformed files. In particular what happens if simulation
            numbers are mixed?

        Parameters
        ----------
        filepath : Path
            Path to the file to load.
        e_acc : np.ndarray
            Accelerating field values in :unit:`V/m`.
        delimiter : str, optional
            Delimiter between columns.

        """
        if delimiter is None:
            delimiter = "\t"
        raw_data = np.loadtxt(filepath, delimiter=delimiter)
        raw_data[:, 2] *= 1e9

        results: list[Spark3DResults] = []

        for i, this_e_acc in enumerate(e_acc, start=1):
            idx_lines = np.where(raw_data[:, 0] == float(i))[0]
            power = raw_data[idx_lines, 1][0]
            time = raw_data[idx_lines, 2]
            num_elec = raw_data[idx_lines, 3]

            results.append(
                Spark3DResults(
                    id=i,
                    e_acc=this_e_acc,
                    time=time,
                    population=num_elec,
                    p_rms=power,
                    plotter=self._plotter,
                    period=self._period,
                )
            )

        return results

    def _from_csv(
        self,
        filepath: Path,
        e_acc: np.ndarray,
        delimiter: str | None = " ",
        **kwargs,
    ) -> list[Spark3DResults]:
        """
        Create several :class:`.Spark3DResults` from :file:`time_results.csv`.

        Right-click on ``Multipactor results``, ``Export to CSV``.
        These files are manually produced by the user. ``CSV`` files look like
        this::

            0      1000    1000    1000    1000
            1e-9   1010    900     999     1001
            2e-9   1020    500     998     1002
            3e-9   1040    100     990     1003
            4e-9   1050    0       950     1004
            ...

        There are no headers. The first column holds the time in seconds.
        Following columns hold the number of electrons for every simulation
        (one simulation on one column).

        .. note::
            In order to be consistent with CST import, we remove the end of the
            simulations, when the population is 0.

        Parameters
        ----------
        filepath :
            Path to the file to load.
        e_acc :
            Accelerating field values in :unit:`V/m`.
        delimiter :
            Delimiter between columns.

        """
        if delimiter is None:
            delimiter = " "
        raw_data = np.loadtxt(filepath, delimiter=delimiter)
        time = raw_data[:, 0] * 1e9
        p_rms = None

        results: list[Spark3DResults] = []

        for idx_col, this_e_acc in enumerate(e_acc, start=1):
            population = raw_data[:, idx_col]
            results.append(
                Spark3DResults(
                    id=idx_col,
                    e_acc=this_e_acc,
                    time=time,
                    population=population,
                    p_rms=p_rms,
                    plotter=self._plotter,
                    trim_trailing=True,
                    period=self._period,
                )
            )

        return results
