"""Define types and type hints."""

from typing import Literal

#: :class:`.SimulationResults` attributes stored as float.
DATA_0D = ("id", "e_acc", "p_rms", "alpha")
#: :class:`.SimulationResults` attributes stored as float.
DATA_0D_t = Literal["id", "e_acc", "p_rms", "alpha"]

#: :class:`.SimulationResults` attributes stored as 1D arrays.
DATA_1D = ("time", "population", "modelled_population")
#: :class:`.SimulationResult` attributes stored as 1D arrays.
DATA_1D_t = Literal["time", "population", "modelled_population"]

#: :class:`.CSTSimulationResults` attributes if :class:`.ParticleMonitor` was
# defined
PARTICLE_0D = ("emission_energy", "collision_energy", "collision_angle")
#: :class:`.CSTSimulationResults` attributes if :class:`.ParticleMonitor` was
# defined
PARTICLE_0D_t = Literal[
    "emission_energy", "collision_energy", "collision_angle"
]

#: :class:`.CSTSimulationResults` attributes if :class:`.ParticleMonitor` was
# defined
PARTICLE_3D = ("trajectory", "collision_distribution", "emission_distribution")
#: :class:`.CSTSimulationResults` attributes if :class:`.ParticleMonitor` was
# defined
PARTICLE_3D_t = Literal[
    "trajectory", "collision_distribution", "emission_distribution"
]

#: Conversion factors from the accepted accelerating field units to V/m.
E_ACC_TO_V_PER_M = {"V/m": 1.0, "kV/m": 1e3, "MV/m": 1e6}
#: Accepted units for the accelerating field.
E_ACC_UNIT_t = Literal["V/m", "kV/m", "MV/m"]

#: Conversion factors from the accepted power units to W.
P_RMS_TO_W = {"W": 1.0, "kW": 1e3, "MW": 1e6}
#: Accepted units for the RMS power.
P_RMS_UNIT_t = Literal["W", "kW", "MW"]
