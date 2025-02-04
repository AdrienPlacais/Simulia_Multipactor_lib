"""Define an object to store CST simulation results.

.. note::
    As for now, it can only load data stored in a single file. For Position
    Monitor exports (one file = one time step), see dedicated package
    ``PositionMonitor``.

.. todo::
    Evaluate expressions such as ``param2 = 2 * param1``

"""

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
        e_acc_file: str = "E_acc in MV per m.txt",
        p_rms_file: str | None = None,
        **kwargs,
    ) -> None:
        """Instantiate object.

        If necessary, override default ``e_acc`` filename.

        Parameters
        ----------
        plotter : Plotter
            Object to plot data.
        e_acc_file : str, optional
            Name of the file where the value of the accelerating field in MV/m
            is written. If not provided, we use default
            ``"E_acc in MV per m.txt"``. Note that this file must exist.
        e_acc_file : str, optional
            Name of the file where the value of the RMS power in W is written.
            If not provided, we do not load RMS power.

        """
        self._e_acc_file = e_acc_file
        self._p_rms_file = p_rms_file
        return super().__init__(*args, plotter=plotter, **kwargs)

    @property
    def mandatory_files(self) -> tuple[str, str, str]:
        """Give the name of the mandatory files."""
        return (
            self._e_acc_file,
            self._parameters_file,
            self._time_population_file,
        )

    def _from_simulation_folder(
        self, folderpath: Path, delimiter: str = "\t"
    ) -> CSTResults:
        """Instantiate results from a :file:`mmdd-xxxxxxx` folder.

        The expected structure is the following::

            mmdd-xxxxxxx
            ├── 'Adimensional e.txt'
            ├── 'Adimensional h.txt'
            ├── 'E_acc in MV per m.txt'           # Mandatory
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
                    f"{filename = } was not found. However, I found "
                    f"{pformat(list(raw_results.keys()))}"
                )

        e_acc = raw_results.pop(no_extension(self._e_acc_file))
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

    def from_simulation_folders(
        self, master_folder: Path, delimiter: str = "\t"
    ) -> list[CSTResults]:
        """Load all :file:`mmdd-xxxxxxx` folders in ``master_folder``."""
        folders = list(master_folder.iterdir())
        return [
            self._from_simulation_folder(folder, delimiter=delimiter)
            for folder in folders
        ]
