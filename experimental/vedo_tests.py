#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 23 13:40:42 2023.

@author: placais

.. todo::
    plot trajectories in 3d
    showcase collision
    histogram impacts

"""
from pathlib import Path

import numpy as np

import vedo
from vedo import Mesh, Points

from multipactor.particle_monitor.particle_monitor import ParticleMonitor

vedo.close()
plt = vedo.Plotter()


def plot_mesh(stl_file: Path,
              alpha: float = .3) -> Mesh:
    mesh = Mesh(stl_file, alpha=alpha)
    return mesh


def plot_single_trajectory(positions: np.ndarray,
                           color: tuple[float, float, float] | None = None
                           ) -> Points:
    points = Points(positions, c=color)
    return points


def add_shadows(shadow_positions: tuple[float, float, float],
                plt: vedo.Plotter,
                ) -> None:
    # plt.add_shadows()
    # for vedo_object in plt:
    #     vedo_object.add_shadow('x', shadow_positions[0])
    #     vedo_object.add_shadow('y', shadow_positions[1])
    #     vedo_object.add_shadow('z', shadow_positions[2])
    return


basepath = Path("../examples/cst/WR75_reduced/")
stl_file = Path(basepath, "wr75.stl")
plt += plot_mesh(stl_file)

folder, delimiter = Path(basepath, "Export/3d"), None
my_particle_monitor = ParticleMonitor(folder, delimiter=delimiter)

for i in range(1, 100):
    toplot = my_particle_monitor[i]
    positions = toplot.pos
    plt += plot_single_trajectory(positions)

# add_shadows((12., 5., 17.), *plt)
plt.show(axes=1)
