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
from simultipac.particle_monitor.particle_monitor import (
    FILTER_FUNC,
    FILTER_KEY,
    ParticleMonitor,
)
from simultipac.plotter.default import DefaultPlotter
from simultipac.plotter.plotter import Plotter
from simultipac.simulation_results.simulation_results import (
    SimulationResults,
    SimulationResultsFactory,
)
from simultipac.types import PARTICLE_0D_t, PARTICLE_3D_t


class MissingFileError(Exception):
    """Error raised when a mandatory CST file was not found."""


class CSTResults(SimulationResults):
    """Store a single CST simulation results."""

    def __init__(
        self,
        id: int,
        e_acc: float,
        time: np.ndarray,
        population: np.ndarray,
        p_rms: float | None = None,
        plotter: Plotter | None = None,
        trim_trailing: bool = False,
        period: float | None = None,
        parameters: dict[str, float | bool | str] | None = None,
        stl_alpha: float | None = None,
        particle_monitor: ParticleMonitor | None = None,
        **kwargs,
    ) -> None:
        """Instantiate, post-process.

        Parameters
        ----------
        id :
            Unique simulation identifier.
        e_acc :
            Accelerating field in :unit:`V/m`.
        time :
            Time in :unit:`ns`.
        population :
            Evolution of population with time. Same shape as ``time``.
        p_rms :
            RMS power in :unit:`W`.
        plotter :
            An object allowing to plot data.
        trim_trailing :
            To remove the last simulation points, when the population is 0.
            Used with SPARK3D (``CSV`` import) for consistency with CST.
        period :
            RF period in :unit:`ns`. Mandatory for exponential growth fits.
        parameters :
            Additional information on the simulation. Typically, value of
            magnetic field, number of PIC cells, simulation flags...
        stl_path :
            Path to the ``STL`` file holding the 3D structure of the system.
            If given, we automatically load it.
        stl_alpha :
            Transparency for the 3D mesh.
        particle_monitor :
            Stores all particle monitor data.

        """
        super().__init__(
            id=id,
            e_acc=e_acc,
            time=time,
            population=population,
            p_rms=p_rms,
            plotter=plotter,
            trim_trailing=trim_trailing,
            period=period,
            parameters=parameters,
            stl_alpha=stl_alpha,
            **kwargs,
        )
        self._particle_monitor: ParticleMonitor
        if particle_monitor is not None:
            self._particle_monitor = particle_monitor

    def hist(
        self,
        x: PARTICLE_0D_t,
        bins: int = 200,
        hist_range: tuple[float, float] | None = None,
        plotter: Plotter | None = None,
        filter: FILTER_KEY | FILTER_FUNC | None = None,
        **kwargs,
    ) -> Any:
        """Create a histogram.

        Parameters
        ----------
        x :
            Name of the data to plot.
        bins :
            Number of histogram bins.
        hist_range :
            Lower and upper value for the histogram.
        plotter :
            Object creating the plots.
        filter :
            To plot only some of the particles.

        """
        return self._particle_monitor.hist(
            x=x,
            bins=bins,
            hist_range=hist_range,
            plotter=plotter,
            filter=filter,
            **kwargs,
        )

    def plot_3d(self, key: PARTICLE_3D_t, **kwargs) -> Any:
        if key == "trajectory":
            return self.plot_trajectories(**kwargs)

    def plot_trajectories(
        self,
        emission_color: str | None = None,
        collision_color: str | None = None,
        lw: int = 7,
        r: int = 8,
        plotter: Plotter | None = None,
        filter: FILTER_KEY | FILTER_FUNC | None = None,
        **kwargs,
    ) -> Any:
        """Plot trajectories in 3D.

        Parameters
        ----------
        emission_color :
            If provided, the first known position is colored with this color.
        collision_color :
            If provided, the last known position is colored with this color.
        collision_point :
            If provided and ``collision_color`` is not ``None``, we plot this
            point instead of the last of ``points``. This is useful when the
            extrapolated time is large, and actuel collision point may differ
            significantly from last position points.
        lw :
            Trajectory line width.
        r :
            Size of the emission/collision points.
        plotter :
            An object allowing to plot data.
        filter :
            To select the particles to be plotted.

        """
        return self._particle_monitor.plot_trajectories(
            emission_color=emission_color,
            collision_color=collision_color,
            lw=lw,
            r=r,
            plotter=plotter,
            filter=filter,
            **kwargs,
        )

    def plot_mesh(self, *args, **kwargs) -> Any:
        """Plot the stored mesh."""
        return self._particle_monitor.plot_mesh(*args, **kwargs)

    def plot_trajectories(
        self,
        emission_color: str | None = None,
        collision_color: str | None = None,
        lw: int = 7,
        r: int = 8,
        plotter: Plotter | None = None,
        filter: FILTER_KEY | FILTER_FUNC | None = None,
        **kwargs,
    ) -> Any:
        """Plot trajectories in 3D.

        Parameters
        ----------
        emission_color :
            If provided, the first known position is colored with this color.
        collision_color :
            If provided, the last known position is colored with this color.
        collision_point :
            If provided and ``collision_color`` is not ``None``, we plot this
            point instead of the last of ``points``. This is useful when the
            extrapolated time is large, and actuel collision point may differ
            significantly from last position points.
        lw :
            Trajectory line width.
        r :
            Size of the emission/collision points.
        plotter :
            An object allowing to plot data.
        filter :
            To select the particles to be plotted.

        """
        return self._particle_monitor.plot_trajectories(
            emission_color=emission_color,
            collision_color=collision_color,
            lw=lw,
            r=r,
            plotter=plotter,
            filter=filter,
            **kwargs,
        )


class CSTResultsFactory(SimulationResultsFactory):
    """Define an object to easily instantiate :class:`.CSTResults`."""

    _parameters_file = "Parameters.txt"
    _time_population_file = "Particle vs. Time.txt"

    def __init__(
        self,
        *args,
        plotter: Plotter | None = None,
        freq_ghz: float | None = None,
        e_acc_parameter: Sequence[str] = (
            "E_acc",
            "e_acc",
            "accelerating_field",
        ),
        e_acc_file_mv_m: str = "E_acc in MV per m.txt",
        p_rms_file: str | None = None,
        stl_path: Path | str | None = None,
        stl_alpha: float | None = None,
        **kwargs,
    ) -> None:
        """Instantiate object.

        If necessary, override default ``e_acc`` filename.

        Parameters
        ----------
        plotter :
            Object to plot data.
        freq_ghz :
            RF frequency in GHz. Used to compute RF period, which is mandatory
            for exp growth fitting.
        e_acc_parameter :
            The possible names of the accelerating field in
            :file:`Parameters.txt`; we try all of them sequentially, and resort
            to taking it from a file if it was not successful. You can pass in
            an empty tuple to force the use of the file.
        e_acc_file_mv_m :
            Name of the file where the value of the accelerating field in
            :unit:`MV/m` is written. This is a fallback, we prefer getting
            accelerating field from the :file:`Parameters.txt` file.
        e_acc_file :
            Name of the file where the value of the RMS power in W is written.
            If not provided, we do not load RMS power.
        stl_path :
            Path to the `STL` file describing the geometry. Used by
            :class:`.ParticleMonitor` to compute emission and collision angles,
            and realize 3D plots.
        stl_alpha :
            Transparency for the 3D mesh.

        """
        if plotter is None:
            plotter = DefaultPlotter()
        self._e_acc_parameter = e_acc_parameter
        self._e_acc_file_mv_m = e_acc_file_mv_m
        self._p_rms_file = p_rms_file
        return super().__init__(
            *args,
            plotter=plotter,
            freq_ghz=freq_ghz,
            stl_path=stl_path,
            stl_alpha=stl_alpha,
            **kwargs,
        )

    @property
    def mandatory_files(self) -> set[str]:
        """Give the name of the mandatory files."""
        mandatory = {self._parameters_file, self._time_population_file}
        if len(self._e_acc_parameter) == 0:
            mandatory.add(self._e_acc_file_mv_m)
        return mandatory

    def from_simulation_folder(
        self,
        folderpath: Path,
        delimiter: str = "\t",
        folder_particle_monitor: str | Path | None = None,
        load_first_n_particles: int | None = None,
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

        If you want to load particle monitor data, you must provide
        ``folder_particle_monitor`` where all particle monitors are stored.
        Typical structure is::

            folder_particle_monitor
            ├──'position  monitor 1_0.117175810039043.txt'
            ├──'position  monitor 1_0.156234413385391.txt'
            ├──'position  monitor 1_0.19529302418232.txt'
            ├──'position  monitor 1_0.232905015349388.txt'
            ├──'position  monitor 1_0.271963626146317.txt'
            ├──...
            └──'position  monitor 1_7.81172066926956E-02.txt'

        Parameters
        ----------
        folderpath :
            Path to a :file:`mmdd-xxxxxxx` folder, holding the results of a
            single simulation among a parametric simulation export.
        delimiter :
            Delimiter between two columns.
        folder_particle_monitor :
            Holds all the particle monitor files.
        load_first_n_particles :
            If provided, we only load the ``load_first_n_particles`` first
            particles. Useful for debugging/speeding up.

        Returns
        -------
        results : CSTResults
            Instantiated object.

        """
        assert folderpath.is_dir(), f"{folderpath = } does not exist."
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

        particle_monitor = None
        if folder_particle_monitor is not None:
            particle_monitor = ParticleMonitor.from_folder(
                folder_particle_monitor,
                plotter=self._plotter,
                stl_path=self._stl_path,
                stl_alpha=self._stl_alpha,
                load_first_n_particles=load_first_n_particles,
            )
        results = CSTResults(
            id=id,
            e_acc=e_acc,
            time=time,
            population=population,
            p_rms=p_rms,
            plotter=self._plotter,
            period=self._period,
            parameters=raw_results.pop(no_extension(self._parameters_file)),
            particle_monitor=particle_monitor,
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
        self,
        master_folder: Path,
        delimiter: str = "\t",
    ) -> list[CSTResults]:
        """Load all :file:`mmdd-xxxxxxx` folders in ``master_folder``.

        Note
        ----
        Loading of :class:`.ParticleMonitor` for multiple simulations is
        currently not supported.

        """
        folders = list(master_folder.iterdir())
        return [
            self.from_simulation_folder(folder, delimiter=delimiter)
            for folder in folders
        ]
