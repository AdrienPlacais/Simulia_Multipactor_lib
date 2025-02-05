"""Define a default plotter."""

from typing import Any

import pandas as pd
from matplotlib.axes import Axes
from matplotlib.typing import ColorType
from numpy.typing import NDArray

from simultipac.constants import markdown
from simultipac.plotter.plotter import Plotter


class DefaultPlotter(Plotter):
    """An object using maptlotlib for 2D, Vedo for 3D."""

    def plot(
        self,
        data: pd.DataFrame,
        x: str,
        y: str,
        grid: bool = True,
        axes: Axes | NDArray[Any] | None = None,
        xlabel: str | None = None,
        ylabel: str | None = None,
        label: str | None = None,
        **kwargs,
    ) -> tuple[Axes | NDArray[Any], ColorType]:
        """Plot 2D data.

        Parameters
        ----------
        data : pd.DataFrame
            Holds all data to plot.
        x, y : str
            Name of column in ``data`` for x/y.
        grid : bool, optional
            If grid should be plotted. Default is True.
        axes : Axes | NDArray[Any] | None, optional
            Axes to re-use, if provided. The default is None (plot on new
            axis).
        xlabel, ylabel : str | None, optional
            Name of the labels. If not provided, we use the markdown equivalent
            of x/y, if defined in :data:`.markdown`.
        label : str | None, optional
            If provided, overrides the legend. Useful when several simulations
            are shown on the same plot.
        kwargs :
            Other keyword passed to the ``pd.DataFrame.plot`` method.

        Returns
        -------
        axes : Axes | NDArray[Any]
            Objects created by the ``pd.DataFrame.plot`` method.
        color : ColorType
            Color used for the plot.

        """
        if xlabel is None:
            xlabel = markdown.get(x, x)
        if ylabel is None:
            ylabel = markdown.get(y, y)
        axes = data.plot(
            x=x,
            y=y,
            grid=grid,
            ax=axes,
            xlabel=xlabel,
            ylabel=ylabel,
            label=label,
            **kwargs,
        )
        assert axes is not None
        color = self._get_color_from_last_plot(axes)
        return axes, color

    def _get_color_from_last_plot(
        self, axes: Axes | NDArray[Any]
    ) -> ColorType:
        """Get the color used for the last plot."""
        ax = axes if isinstance(axes, Axes) else axes[-1]
        assert isinstance(ax, Axes)
        lines = ax.get_lines()
        color = lines[-1].get_color()
        return color

    def plot_3d(self, *args, **kwargs) -> Any:
        """Create a 3D plot."""
        raise NotImplementedError
