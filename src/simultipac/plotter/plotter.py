"""Define the generic :class:`Plotter`."""

from abc import ABC, abstractmethod
from typing import Any

import pandas as pd


class Plotter(ABC):
    """An object used to plot data."""

    @abstractmethod
    def plot(self, data: pd.DataFrame, *args, **kwargs) -> Any:
        """Plot data and return axes object."""

    @abstractmethod
    def plot_3d(self, *args, **kwargs) -> Any:
        """Create a 3D plot."""
