"""Define types and type hints."""

from typing import Literal

#: :class:`.SimulationResult` attributes stored as float.
DATA_0D = ("id", "e_acc", "p_rms", "alpha")
#: :class:`.SimulationResult` attributes stored as float.
DATA_0D_t = Literal["id", "e_acc", "p_rms", "alpha"]

#: :class:`.SimulationResult` attributes stored as 1D arrays.
DATA_1D = ("time", "population", "modelled_population")
#: :class:`.SimulationResult` attributes stored as 1D arrays.
DATA_1D_t = Literal["time", "population", "modelled_population"]
