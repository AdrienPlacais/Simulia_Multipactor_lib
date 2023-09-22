#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 17:40:54 2023.

@author: placais

This script is a first attempt to load ``.stl`` files.

"""
import matplotlib.pyplot as plt
import numpy as np
from numpy.random._generator import Generator

from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d.axes3d import Axes3D
from multipactor.experimental.collision import (
    vectorized_part_mesh_intersections)
from stl import mesh


# =============================================================================
# Cube generation
# =============================================================================
def _generate_data_for_half_cube() -> np.ndarray:
    # Draw a cube
    data = np.zeros(6, dtype=mesh.Mesh.dtype)

    # Top
    data["vectors"][0] = np.array([[0, 1, 1], [1, 0, 1], [0, 0, 1]])
    data["vectors"][1] = np.array([[1, 0, 1], [0, 1, 1], [1, 1, 1]])
    # Front face
    data["vectors"][2] = np.array([[1, 0, 0], [1, 0, 1], [1, 1, 0]])
    data["vectors"][3] = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 0]])
    # Left face
    data["vectors"][4] = np.array([[0, 0, 0], [1, 0, 0], [1, 0, 1]])
    data["vectors"][5] = np.array([[0, 0, 0], [0, 0, 1], [1, 0, 1]])
    data["vectors"] -= 0.5

    return data


def _half_cube_data_to_cube(data: np.ndarray) -> mesh.Mesh:
    """Generate the real cube."""
    cube_back = mesh.Mesh(data.copy())
    cube_front = mesh.Mesh(data.copy())
    cube_back.rotate([0.5, 0.0, 0.0], np.pi * 0.5)
    cube_back.rotate([0.0, 0.5, 0.0], np.pi * 0.5)
    cube_back.rotate([0.5, 0.0, 0.0], np.pi * 0.5)

    cube = mesh.Mesh(
        np.concatenate([
            cube_back.data.copy(),
            cube_front.data.copy(),
        ]))

    return cube


# =============================================================================
# Plotting
# =============================================================================
def _create_3d_fig() -> Axes3D:
    """Create the 3d plot."""
    fig = plt.figure(1)
    axes: Axes3D = fig.add_subplot(projection="3d",
                                   proj_type="ortho")
    axes.set_xlabel(r"$x$")
    axes.set_ylabel(r"$y$")
    axes.set_zlabel(r"$z$")

    return axes


def _plot_mesh(to_plot: np.ndarray, axes: Axes3D, **kwargs) -> None:
    """Plot the mesh with proper scaling."""
    collection = mplot3d.art3d.Poly3DCollection(to_plot, **kwargs)
    axes.add_collection3d(collection)
    plt.show()


def _plot_points(points: np.ndarray, axes: Axes3D, **kwargs) -> None:
    """Plot the given points."""
    if points.ndim == 1:
        points = np.expand_dims(points, 0)
    axes.scatter(points[:, 0], points[:, 1], points[:, 2], **kwargs)
    plt.show()


def _plot_lines(points: np.ndarray, axes: Axes3D, **kwargs) -> None:
    """Plot the given points."""
    axes.plot(points[:, 0], points[:, 1], points[:, 2], **kwargs)
    plt.show()


def _equal_scale(truc: mesh.Mesh, axes: Axes3D) -> None:
    """Revert back to equal scaling."""
    scale = truc.points.flatten()
    axes.auto_scale_xyz(scale, scale, scale)
    plt.show()


# =============================================================================
# Generate fake rays/particles for debug
# =============================================================================
def _generate_random_parts(
    truc: mesh.Mesh,
    n_part: int = 11,
    max_distance: float | None = None,
    seed: int | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Generate a random set of particles that can cross (or not) the cube."""
    rng: Generator = np.random.default_rng(seed=seed)
    max_, min_ = 1.1 * truc.max_, 1.1 * truc.min_
    origins = rng.random((n_part, 3)) * (max_ - min_) + min_
    directions = rng.random((n_part, 3))
    norm = np.linalg.norm(directions, axis=1)
    directions /= norm[:, np.newaxis]

    # force something different
    # origins = np.zeros((n_part, 3))
    # directions = np.array([[0., np.sqrt(2.) / 2., np.sqrt(2.) / 2.],])

    if max_distance is None:
        max_distance = 0.8 * (np.mean(max_) - np.mean(min_))
    distances: np.ndarray[np.float64] = rng.random(n_part) * max_distance

    # Two (n_part, 3) to single (n_part, 2, 3)
    trajectories: np.ndarray[np.float64] = np.stack(
        [origins, origins + max_distance * directions], axis=1)

    return origins, directions, trajectories, distances


def _test_vectorized_parts(truc: mesh.Mesh, axes: Axes3D, n_part: int) -> None:
    """Generate several particles and test it with vect function."""
    args = _generate_random_parts(truc, n_part=n_part, seed=None)
    origins, directions, trajectories, distances = args

    for traj in trajectories:
        _plot_lines(traj, axes, **{"c": "r"})
        _plot_points(traj, axes, **{"c": "r", "s": 50})

    args = vectorized_part_mesh_intersections(origins, directions, truc,
                                              distances=distances)
    collisions, distances_to_collision, impact_angles = args
    impact_angles = np.rad2deg(impact_angles)
    print(f"{impact_angles = }")

    for i, (collision, dist_to_coll, origin, direction) in enumerate(
            zip(collisions, distances_to_collision, origins, directions)):
        impacted_cells = truc.vectors[collision]
        print(f"Particle {i} impacted {len(impacted_cells)} cells.")
        _plot_mesh(impacted_cells, axes, **{"facecolors": "b",
                                            "edgecolors": "k",
                                            "alpha": 0.7,
                                            },)

        if len(impacted_cells) > 0:
            impact_points = np.array([
                origin + distance * direction
                for distance in dist_to_coll if distance is not None
            ])
            _plot_points(impact_points, axes, **{"c": "k",
                                                 "s": 100,
                                                 "marker": "s"
                                                 })


# =============================================================================
# Main script
# =============================================================================

if __name__ == "__main__":
    debug = True

    axes = _create_3d_fig()

    data = _generate_data_for_half_cube()
    cube = _half_cube_data_to_cube(data)
    my_mesh = cube

    if not debug:
        my_mesh = mesh.Mesh.from_file("tesla.stl")

    _plot_mesh(my_mesh.vectors, axes, **{"edgecolors": "k",
                                         "linewidths": 0.1,
                                         "facecolors": "g",
                                         "alpha": 0.3,
                                         },
               )
    _test_vectorized_parts(my_mesh, axes, n_part=1)

    _equal_scale(my_mesh, axes)
