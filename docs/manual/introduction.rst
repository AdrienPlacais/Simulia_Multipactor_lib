Introduction
============
This library is a set of tool to treat results from CST and SPARK3D.
All illustrations shown below are produced with the scripts from the Jupyter notebook examples.


Compute exponential growth factors
**********************************
From SPARK3D
------------

.. image:: images/exp_growth_spark.png
   :alt: Evolution of exponential growth factor with accelerating field

From CST
--------

.. image:: images/exp_growth_cst.png
   :alt: Evolution of exponential growth factor with accelerating field

.. note::
   Easy study of the influence of other parameters, such as number of seed electrons in this example.

Treat CST's position monitor data
*********************************
Compute distribution of emission energy
---------------------------------------

.. image:: images/emission_energy_distribution.png
   :alt: Distribution of emission energies

Compute distribution of collision energy
----------------------------------------

.. image:: images/collision_energy_distribution.png
   :alt: Distribution of collision energies

Compute distribution of the impact angles
-----------------------------------------

.. image:: images/collision_angle_distribution.png
   :alt: Distribution of collision angles

.. note::
   In contrary to the collision angle histogram, the collision and emission energy histograms are natively available in CST.

Plot trajectories
-----------------

.. image:: images/trajectories_1.png
   :alt: Plot of some trajectories

.. image:: images/trajectories_2.png
   :alt: Plot of some trajectories

