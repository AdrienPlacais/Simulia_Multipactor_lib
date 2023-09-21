#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 17:40:54 2023.

@author: placais

This script is a first attempt to load ``.stl`` files.

"""
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d.axes3d import Axes3D
from multipactor.experimental.collision import (
    ray_mesh_intersections, vectorized_part_mesh_intersections)
from numpy.random._generator import Generator
from stl import mesh


# =============================================================================
# Cube generation
# =============================================================================
def _generate_data_for__half_cube() -> np.ndarray:
    """Generate data for cube."""
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
    axes: Axes3D = fig.add_subplot(projection="3d")
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
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate a random set of particles that can cross (or not) the cube."""
    rng: Generator = np.random.default_rng(seed=seed)
    # not clean...
    max_, min_ = 1.1 * truc.max_, 1.1 * truc.min_

    part_origin = np.zeros((n_part, 3))
    # part_origin = rng.random(3) * (max_ - min_) + min_
    part_direction = rng.random((n_part, 3))
    part_direction /= np.linalg.norm(part_direction, axis=1)

    if max_distance is None:
        # not clean
        max_distance = 0.8 * (np.mean(max_) - np.mean(min_))

    # Two (n_part, 3) to single (n_part, 2, 3)
    trajectories = np.stack(
        (part_origin, part_origin + max_distance * part_direction), axis=1)

    return part_origin, part_direction, trajectories, max_distance


def _generate_random_ray(
    truc: mesh.Mesh,
    max_distance: float | None = None,
    seed: int | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate a random ray that can cross (or not) the cube."""
    rng = np.random.default_rng(seed=seed)
    # not clean...
    max_, min_ = 1.1 * truc.max_, 1.1 * truc.min_

    ray_origin = np.zeros(3)
    # ray_origin = rng.random(3) * (max_ - min_) + min_
    ray_direction = rng.random(3)
    ray_direction /= np.linalg.norm(ray_direction)

    if max_distance is None:
        # not clean
        max_distance = 0.8 * (np.mean(max_) - np.mean(min_))
    trajectory = np.vstack(
        (ray_origin, ray_origin + max_distance * ray_direction))

    return ray_origin, ray_direction, trajectory, max_distance


def _test_single_ray(truc: mesh.Mesh, axes: Axes3D) -> None:
    """Generate a ray and see if it impacts the given mesh."""
    ray_origin, ray_direction, trajectory, max_distance = _generate_random_ray(
        truc, seed=None)
    _plot_lines(trajectory, axes, **{"c": "r"})
    _plot_points(trajectory, axes, **{"c": "r", "s": 50})

    collisions, distances = ray_mesh_intersections(ray_origin, ray_direction,
                                                   truc, max_distance)

    impacted_cells = truc.vectors[collisions]
    print(f"Number of impacted cells: {len(impacted_cells)}")
    _plot_mesh(
        impacted_cells,
        axes,
        **{
            "facecolors": "b",
            "edgecolors": "k",
            "alpha": 0.7,
        },
    )

    if len(impacted_cells) > 0:
        impact_points = np.array([
            ray_origin + distance * ray_direction for distance in distances
            if distance is not None
        ])
        _plot_points(impact_points, axes, **{
            "c": "k",
            "s": 100,
            "marker": "s"
        })


def _test_vectorized_parts(truc: mesh.Mesh, axes: Axes3D) -> None:
    """Generate several particles and test it with vect function."""
    args = _generate_random_parts(truc, n_part=2, seed=None)
    part_origins, part_directions, trajectories, max_distances = args

    for traj in trajectories:
        _plot_lines(traj, axes, **{"c": "r"})
        _plot_points(traj, axes, **{"c": "r", "s": 50})

    collisions, distances = vectorized_part_mesh_intersections(
        part_origins, part_directions, truc, max_distances=max_distances)

    for i, (
            this_part_impact,
            this_part_dist,
            this_part_orig,
            this_part_dir,
    ) in enumerate(zip(collisions, distances, part_origins, part_directions)):
        impacted_cells = truc.vectors[this_part_impact]
        print(f"Particle {i} impacted {len(impacted_cells)} cells.")
        _plot_mesh(
            impacted_cells,
            axes,
            **{
                "facecolors": "b",
                "edgecolors": "k",
                "alpha": 0.7,
            },
        )

        if len(impacted_cells) > 0:
            impact_points = np.array([
                this_part_orig + distance * this_part_dir
                for distance in this_part_dist if distance is not None
            ])
            _plot_points(impact_points, axes, **{
                "c": "k",
                "s": 100,
                "marker": "s"
            })


# =============================================================================
# Main script
# =============================================================================

if __name__ == "__main__":
    debug = True
    vectorize = False
    axes = _create_3d_fig()

    data = _generate_data_for__half_cube()
    cube = _half_cube_data_to_cube(data)
    my_mesh = cube

    if not debug:
        my_mesh = mesh.Mesh.from_file("tesla.stl")

    _plot_mesh(
        my_mesh.vectors,
        axes,
        **{
            "edgecolors": "k",
            "linewidths": 0.1,
            "facecolors": "g",
            "alpha": 0.3,
        },
    )

    if not vectorize:
        _test_single_ray(my_mesh, axes)

    else:
        _test_vectorized_parts(my_mesh, axes)

    _equal_scale(my_mesh, axes)
