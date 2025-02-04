"""Define the generic :class:`Plotter`."""

from abc import ABC, abstractmethod
from typing import Any

import pandas as pd


class Plotter(ABC):
    """An object used to plot data."""

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
    ) -> Any:
        """Plot 2D data.

        Parameters
        ----------
        data : pd.DataFrame
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
            Axis objects.

        """

    @abstractmethod
    def plot_3d(self, *args, **kwargs) -> Any:
        """Create a 3D plot."""
