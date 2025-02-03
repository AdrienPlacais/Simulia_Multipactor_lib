"""Define a :class:`.Plotter` adapted to 3D plots."""

from typing import Any

import vedo

from simultipac.plotter.plotter import Plotter


class VedoPlotter(Plotter):
    """An object adapted to 3D plotting."""

    supports_3d = True

    def plot_3d(self, *args, **kwargs) -> Any:
        """Create a 3D plot."""
        raise NotImplementedError
