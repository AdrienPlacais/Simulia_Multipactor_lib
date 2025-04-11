"""Define the generic :class:`Plotter`."""

from abc import abstractmethod
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from simultipac.types import PARTICLE_0D_t, PARTICLE_3D_t
from simultipac.util.singleton import SingletonMeta


class Plotter(metaclass=SingletonMeta):
    """An object used to plot data."""

    def __init__(self, *args, **kwargs) -> None:
        return

    @abstractmethod
    def plot(
        self,
        data: pd.DataFrame,
        x: str,
        y: str,
        grid: bool = True,
        axes: Any | None = None,
        xlabel: str | None = None,
        ylabel: str | None = None,
        label: str | None = None,
        **kwargs,
    ) -> tuple[Any, Any]:
        """Plot 2D data.

        Parameters
        ----------
        data : pandas.DataFrame
            Holds all data to plot.
        x, y : str
            Name of column in ``data`` for x/y.
        grid : bool, optional
            If grid should be plotted. Default is True.
        axes : Any | None, optional
            Axes to re-use, if provided. The default is None (plot on new
            axis).
        xlabel, ylabel : str | None, optional
            Name of the labels. If not provided, we use the markdown equivalent
            of x/y, if defined in :data:`.markdown`.
        label : str | None, optional
            If provided, overrides the legend. Useful when several simulations
            are shown on the same plot.
        kwargs :
            Other keyword passed to the actual plot method.

        Returns
        -------
        Any
            Axis object.
        Any
            Color used for the plot.

        """

    @abstractmethod
    def hist(
        self,
        data: pd.DataFrame,
        x: PARTICLE_0D_t,
        bins: int = 200,
        hist_range: tuple[float, float] | None = None,
        **kwargs,
    ) -> Any:
        """Plot a histogram.

        Parameters
        ----------
        data : pandas.DataFrame
            Holds all data to plot.
        x : PARTICLE_0D_t
            Name of the column in ``data`` to plot.
        bins : int, optional
            Number of bins in the histogram. The default is 200.
        hist_range : tuple[float, float] | None, optional
            Lower and upper range for the calculation of the histogram. The
            default is None.
        kwargs :
            Other keyword arguments passed to the actual plot method.

        Returns
        -------
        Any
            Axis object.

        """

    @abstractmethod
    def plot_3d(
        self,
        data: Any,
        key: PARTICLE_3D_t,
        *args,
        **kwargs,
    ) -> Any:
        """Create a 3D plot.

        Parameters
        ----------
        data : Any
            Object storing the data to plot.
        key : PARTICLE_3D_t
            Name/nature of the data to plot.

        """

    @abstractmethod
    def load_mesh(
        self, stl_path: str | Path, stl_alpha: float | None = None, **kwargs
    ) -> Any:
        """Load the 3D mesh.

        Parameters
        ----------
        stl_path : str | Path
            Path to the ``STL`` file.
        stl_alpha : float | None, optional
            Transparency for the mesh. The default is None.

        Returns
        -------
        Any
            Mesh object.

        """

    @abstractmethod
    def plot_mesh(self, mesh: Any, *args, **kwargs) -> Any:
        """Plot a 3D mesh."""

    @abstractmethod
    def plot_trajectory(
        self,
        points: list[NDArray[np.float64]],
        emission_color: str | None = None,
        collision_color: str | None = None,
        collision_point: NDArray[np.float64] = np.array([], dtype=np.float64),
        lw: int = 7,
        r: int = 8,
        **kwargs,
    ) -> Any:
        """Plot the :class:`.Particle` trajectory stored in ``points``.

        Parameters
        ----------
        points :
            List of positions, as returned by :meth:`.Vector.to_list`.
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

        """

    def show(self) -> None:
        """Show the plots that were produced.

        Useful for the bash interface.

        """
        return
