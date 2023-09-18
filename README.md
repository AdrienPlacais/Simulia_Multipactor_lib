# About this package
This package is a set of utils oriented towards multipacting analysis.
In particular:
 - Load particle sweeps and position monitor data from CST Microwave Studio.
 - Load results from SPARK3D.
 - Post-treat electron vs time results from these tools: multipactor trend, multipactor order.
 - Post-treat position monitor data: energy of incoming electrons, impact angle (TODO).

# Installing this package
You will need a recent version of Python (>3.7).
TODO : doc to install `spark3dbatch` library.

The `numpy-stl` module is necessary to study collisions of particles (ParticleMonitor) with walls (impact energy, impact angle).
If you manage your distribution with `pip`, refer to: https://github.com/conda-forge/numpy-stl-feedstock
If you manage your installation with `conda`, refer to: https://github.com/conda-forge/numpy-stl-feedstock
Warning: in the latter case, all your packages must be installed from the `conda-forge` source, which is not the default.
More information: https://www.youtube.com/watch?v=Ul79ihg41Rs

# Tutorial
Examples are provided in the `examples` folder.
