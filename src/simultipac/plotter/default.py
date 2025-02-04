"""Define a default plotter."""

from collections.abc import Sequence
from typing import Any

import matplotlib.pyplot as plt
import vedo
from matplotlib.axes import Axes

from simultipac.plotter.plotter import Plotter


class DefaultPlotter(Plotter):
    """An object using maptlotlib for 2D, Vedo for 3D."""

    def plot(self, *args, **kwargs) -> Axes | Sequence[Axes]:
        """Plot 2D data."""
        raise NotImplementedError

    def plot_3d(self, *args, **kwargs) -> Any:
        """Create a 3D plot."""
        raise NotImplementedError
