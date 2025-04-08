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
