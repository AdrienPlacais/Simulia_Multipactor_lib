"""Define the generic :class:`Plotter`."""

from abc import ABC
from typing import Any

import pandas as pd


class Plotter(ABC):
    """An object used to plot data."""

    supports_3d: bool

    def plot(self, data: pd.DataFrame, *args, **kwargs) -> Any:
        """Plot data and return axes object."""
        raise NotImplementedError
