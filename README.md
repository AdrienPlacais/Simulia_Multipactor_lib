# About this package
This package is a set of utils oriented towards multipacting analysis.
In particular:
 - Load particle sweeps and position monitor data from CST Microwave Studio.
 - Load results from SPARK3D.
 - Post-treat electron vs time results from these tools: multipactor trend, (TODO: multipactor order).
 - Post-treat CST's position monitor data: energy of incoming electrons, impact angle, visualize trajectories.

# Requirements
You will need a recent version of Python (>=3.11).

The `vedo` module is necessary to study collisions of particles (ParticleMonitor) with walls (impact energy, impact angle).
If you manage your distribution with `pip`, refer to: https://vedo.embl.es/docs/vedo.html#install-and-test

If you manage your installation with `conda`, run:
```
conda create -n vedo_env -c conda-forge python=3.11
conda activate vedo_env
conda install -c conda-forge numpy matplotlib pandas scipy vedo
```
Warning: in the latter case, all your packages must be installed from the `conda-forge` source, which is not the default.
You may also want to `conda install -c conda-forge spyder` to have an IDE.
And `conda install -c conda-forge jupyter` to run `.ipynb` examples.

Remember to run `conda activate vedo_env` to activate this environment.
More information: https://www.youtube.com/watch?v=Ul79ihg41Rs

# Install package
The installation workflow is taken from https://daler.github.io/sphinxdoc-test/includeme.html.
Go to where you want the package to be installed:
``cd ~/my/python/packages/``
Clone the `git` repository (you can also download it as `.zip`, but you will not get any update):
``git clone git@gitlab.in2p3.fr:adrien.placais/python-multipactor-library.git``

# Get updates
For package update, go to the package folder and `git pull origin master`.

# Documentation
Documentation is available at: https://adrienplacais.github.io/Simulia_Multipactor_lib/html/index.html#

Integrated following: https://daler.github.io/sphinxdoc-test/includeme.html

# Tutorial
Examples are provided in the `examples` folder.
