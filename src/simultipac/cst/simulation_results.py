"""Define an object to store CST simulation results.

.. note::
    As for now, it can only load data stored in a single file. For Position
    Monitor exports (one file = one time step), see dedicated package
    ``PositionMonitor``.

.. todo::
    Evaluate expressions such as ``param2 = 2 * param1``

.. todo::
    Allow to have P_rms instead of E_acc; E_acc does not make a lot of sense in
    a lot of cases.

"""

import logging
from collections.abc import Sequence
from pathlib import Path
from pprint import pformat
from typing import Any

import numpy as np

from simultipac.cst.helper import (
    get_id,
    mmdd_xxxxxxx_folder_to_dict,
    no_extension,
)
from simultipac.plotter.default import DefaultPlotter
from simultipac.plotter.plotter import Plotter
from simultipac.simulation_results.simulation_results import (
    SimulationResults,
    SimulationResultsFactory,
)


class MissingFileError(Exception):
    """Error raised when a mandatory CST file was not found."""


class CSTResults(SimulationResults):
    """Store a single CST simulation results."""

    def __init__(
        self,
        id: int,
        e_acc: float,
        p_rms: float | None,
        time: np.ndarray,
        population: np.ndarray,
        plotter: Plotter = DefaultPlotter(),
        trim_trailing: bool = False,
        parameters: dict[str, float | bool | str] | None = None,
        **kwargs,
    ) -> None:
        """Instantiate object, with additional ``parameters`` attributes.

        ``parameters`` is used to store CST simulation parameters: value of
        magnetic field, etc.

        """
        self.parameters: dict[str, Any] = (
            {} if parameters is None else parameters
        )
        return super().__init__(
            id,
            e_acc,
            p_rms,
            time,
            population,
            plotter=plotter,
            trim_trailing=trim_trailing,
            **kwargs,
        )


class CSTResultsFactory(SimulationResultsFactory):
    """Define an object to easily instantiate :class:`.CSTResults`."""

    _parameters_file = "Parameters.txt"
    _time_population_file = "Particle vs. Time.txt"

    def __init__(
        self,
        *args,
        plotter: Plotter = DefaultPlotter(),
        e_acc_parameter: Sequence[str] = (
            "E_acc",
            "e_acc",
            "accelerating_field",
        ),
        e_acc_file_mv_m: str = "E_acc in MV per m.txt",
        p_rms_file: str | None = None,
        **kwargs,
    ) -> None:
        """Instantiate object.

        If necessary, override default ``e_acc`` filename.

        Parameters
        ----------
        plotter : Plotter
            Object to plot data.
        e_acc_parameter : Sequence[str], optional
            The possible names of the accelerating field in
            :file:`Parameters.txt`; we try all of them sequentially, and resort
            to taking it from a file if it was not successful. You can pass in
            an empty tuple to force the use of the file.
        e_acc_file_mv_m : str, optional
            Name of the file where the value of the accelerating field in MV/m
            is written. This is a fallback, we prefer getting accelerating
            field from the :file:`Parameters.txt` file.
        e_acc_file : str, optional
            Name of the file where the value of the RMS power in W is written.
            If not provided, we do not load RMS power.

        """
        self._e_acc_parameter = e_acc_parameter
        self._e_acc_file_mv_m = e_acc_file_mv_m
        self._p_rms_file = p_rms_file
        return super().__init__(*args, plotter=plotter, **kwargs)

    @property
    def mandatory_files(self) -> set[str]:
        """Give the name of the mandatory files."""
        mandatory = {self._parameters_file, self._time_population_file}
        if len(self._e_acc_parameter) == 0:
            mandatory.add(self._e_acc_file_mv_m)
        return mandatory

    def _from_simulation_folder(
        self, folderpath: Path, delimiter: str = "\t"
    ) -> CSTResults:
        """Instantiate results from a :file:`mmdd-xxxxxxx` folder.

        The expected structure is the following::

            mmdd-xxxxxxx
            ├── 'Adimensional e.txt'
            ├── 'Adimensional h.txt'
            ├── 'E_acc in MV per m.txt'           # Mandatory if E_acc not in :file:`Parameters.txt`
            ├──  Parameters.txt                   # Mandatory
            ├── 'ParticleInfo [PIC]'
            │   ├── 'Emitted Secondaries.txt'
            │   └── 'Particle vs. Time.txt'       # Mandatory
            ├── 'TD Number of mesh cells.txt'
            └── 'TD Total solver time.txt'

        Non-mandatory files data will be loaded in the ``parameters``
        attribute.

        Parameters
        ----------
        folderpath : Path
            Path to a :file:`mmdd-xxxxxxx` folder, holding the results of a
            single simulation among a parametric simulation export.
        delimiter : str, optional
            Delimiter between two columns. The default is a tab character.

        """
        id = get_id(folderpath)
        raw_results = mmdd_xxxxxxx_folder_to_dict(folderpath, delimiter)

        for filename in self.mandatory_files:
            if no_extension(filename) not in raw_results:
                raise MissingFileError(
                    f"{filename = } was not found in {folderpath}. However, I "
                    f"found {pformat(list(raw_results.keys()))}"
                )

        e_acc = self._pop_e_acc(raw_results, folderpath)
        part_time = raw_results.pop(no_extension(self._time_population_file))
        time, population = part_time[:, 0], part_time[:, 1]
        p_rms = (
            raw_results.pop(no_extension(self._p_rms_file))
            if self._p_rms_file
            else None
        )
        results = CSTResults(
            id=id,
            e_acc=e_acc,
            p_rms=p_rms,
            time=time,
            population=population,
            plotter=self._plotter,
        )
        return results

    def _pop_e_acc(self, raw_results: dict[str, Any], folder: Path) -> float:
        """Pop the value of the accelerating field from ``raw_results.``

        First, we try to get it from the :file:`Parameters.txt` under the names
        listed in ``self._e_acc_parameter``. If was not found, we look into the
        ``self._e_acc_file_mv_m`` file.

        """
        parameters = raw_results[no_extension(self._parameters_file)]
        for name in self._e_acc_parameter:
            e_acc = parameters.pop(name, None)
            if e_acc is not None:
                logging.debug(
                    f"{folder}: took accelerating field from {name} in "
                    f"{self._parameters_file}."
                )
                return e_acc

        if self._e_acc_file_mv_m is not None:
            e_acc = raw_results.pop(no_extension(self._e_acc_file_mv_m), None)
            if e_acc is not None:
                logging.debug(
                    f"{folder}: took accelerating field from "
                    "{self._e_acc_file_mv_m} file. Multiplied it by 1e6."
                )
                return e_acc * 1e-6

        raise ValueError(
            f"Could not find accelerating field in {folder}. Tried to look for"
            f" {self._e_acc_parameter = } key in Parameters.txt, and then for "
            f"a file named {self._e_acc_file_mv_m = }"
        )

    def from_simulation_folders(
        self, master_folder: Path, delimiter: str = "\t"
    ) -> list[CSTResults]:
        """Load all :file:`mmdd-xxxxxxx` folders in ``master_folder``."""
        folders = list(master_folder.iterdir())
        return [
            self._from_simulation_folder(folder, delimiter=delimiter)
            for folder in folders
        ]
