"""Define a base object to store a multipactor simulation results."""

from abc import ABC
from dataclasses import dataclass

import numpy as np


@dataclass
class SimulationResults(ABC):
    """Store a single simulation results."""

    id: int
    acc_field: float
    p_rms: float
    time: np.ndarray
    population: np.ndarray
