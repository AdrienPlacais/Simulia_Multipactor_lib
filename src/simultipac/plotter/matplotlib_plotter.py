"""Define a plotter adapted to 2D data."""

from collections.abc import Sequence

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from simultipac.plotter.plotter import Plotter


class MatplotlibPlotter(Plotter):
    """An object for 2D data."""

    supports_3d = False

    def plot(self, *args, **kwargs) -> Axes | Sequence[Axes]:
        """Plot 2D data."""
        raise NotImplementedError
