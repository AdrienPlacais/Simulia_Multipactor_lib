#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 17:40:54 2023.

@author: placais

This script is a first attempt to load ``.stl`` files.

"""
import numpy
from stl import mesh
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt

my_mesh = mesh.Mesh.from_file('tesla.stl')

fig = plt.figure()
axes = fig.add_subplot(projection='3d')
axes.add_collection3d(mplot3d.art3d.Poly3DCollection(my_mesh.vectors))

scale = my_mesh.points.flatten()
axes.auto_scale_xyz(scale, scale, scale)
plt.show()
