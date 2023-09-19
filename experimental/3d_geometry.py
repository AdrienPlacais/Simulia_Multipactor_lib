#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 17:40:54 2023.

@author: placais

This script is a first attempt to load ``.stl`` files.

"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes._axes import Axes

from stl import mesh
from mpl_toolkits import mplot3d


# =============================================================================
# Cube generation
# =============================================================================
def generate_data_for_half_cube() -> np.ndarray:
    """Generate data for cube."""
    # Draw a cube
    data = np.zeros(6, dtype=mesh.Mesh.dtype)

    # Top
    data['vectors'][0] = np.array([[0, 1, 1],
                                   [1, 0, 1],
                                   [0, 0, 1]])
    data['vectors'][1] = np.array([[1, 0, 1],
                                   [0, 1, 1],
                                   [1, 1, 1]])
    # Front face
    data['vectors'][2] = np.array([[1, 0, 0],
                                   [1, 0, 1],
                                   [1, 1, 0]])
    data['vectors'][3] = np.array([[1, 1, 1],
                                   [1, 0, 1],
                                   [1, 1, 0]])
    # Left face
    data['vectors'][4] = np.array([[0, 0, 0],
                                   [1, 0, 0],
                                   [1, 0, 1]])
    data['vectors'][5] = np.array([[0, 0, 0],
                                   [0, 0, 1],
                                   [1, 0, 1]])
    data['vectors'] -= .5
    return data


def half_cube_data_to_cube(data: np.ndarray) -> mesh.Mesh:
    """Generate the real cube."""
    cube_back = mesh.Mesh(data.copy())
    cube_front = mesh.Mesh(data.copy())
    cube_back.rotate([0.5, 0.0, 0.0], np.pi * .5)
    cube_back.rotate([0.0, 0.5, 0.0], np.pi * .5)
    cube_back.rotate([0.5, 0.0, 0.0], np.pi * .5)

    cube = mesh.Mesh(np.concatenate([cube_back.data.copy(),
                                     cube_front.data.copy(),
                                     ]))
    return cube


# =============================================================================
# Trajectory for my case
# =============================================================================
def generate_linear_trajectory(start: np.ndarray, stop: np.ndarray
                               ) -> np.ndarray:
    """Create points representing a linear trajectory."""
    n_points = 101
    trajectory = np.column_stack((
        np.linspace(start[0], stop[0], n_points),
        np.linspace(start[1], stop[1], n_points),
        np.linspace(start[2], stop[2], n_points)))
    return trajectory


def get_points(mesh: mesh.Mesh) -> np.ndarray:
    """Extract points from mesh, remove doublons."""
    points = mesh.points()
    points = points.reshape([-1, 3])
    return np.unique(points, axis=0)


# =============================================================================
# Collision detection
# =============================================================================
def compute_centroids(truc: mesh.Mesh) -> np.array:
    """
    Compute centre of every triangular mesh cell.

    Parameters
    ----------
    truc : mesh.Mesh
        A random object.

    Returns
    -------
    cent : np.ndarray
        (N, 3) array containing the coordinates of every cell center.

    """
    points = truc.points
    cent = np.column_stack((np.mean(points[:, ::3], axis=1),
                            np.mean(points[:, 1::3], axis=1),
                            np.mean(points[:, 2::3], axis=1),
                            ))
    return cent


def distance_to_centroids(trajectory: np.ndarray, centroids: np.ndarray
                          ) -> np.ndarray:
    """
    Get distance at every time step between particle and every mesh.

    Parameters
    ----------
    trajectory : np.ndarray
        (M, 3) array holding position of a particle at several time steps.
    centroids : np.ndarray
        (N, 3) array containing the coordinates of every cell center.

    Returns
    -------
    distance_matrix : np.ndarray
        (N, M) array holding the distance between particle and every centroid
        at every time step.

    """
    n_cells = centroids.shape[0]
    n_time_steps = trajectory.shape[0]
    distance_matrix = np.zeros((n_cells, n_time_steps))

    for i, cell_center in enumerate(centroids):
        for j, position in enumerate(trajectory):
            distance_matrix[i, j] = np.linalg.norm(cell_center - position)
    return distance_matrix


def get_collision(trajectory: np.ndarray, truc: mesh.Mesh
                  ) -> tuple[np.ndarray, int, int]:
    """Detect the collision between trajectory and ``truc``."""
    centroids = compute_centroids(truc)
    distances = distance_to_centroids(trajectory, centroids)

    cell_idx, time_idx = np.unravel_index(np.argmin(distances),
                                          shape=distances.shape)
    min_distance = distances[cell_idx, time_idx]

    print(f"Collision on cell number {cell_idx} (centroid "
          f"{centroids[cell_idx]})\nat time idx {time_idx} (pos "
          f"{trajectory[time_idx]}).\nCorresp distance is {min_distance}.")
    return min_distance, cell_idx, time_idx


# =============================================================================
# Plotting
# =============================================================================
def create_3d_fig() -> tuple[Figure, Axes]:
    """Create the 3d plot."""
    fig = plt.figure(1)
    axes = fig.add_subplot(projection='3d')
    return fig, axes


def plot_mesh(to_plot: np.array, axes: Axes, **kwargs) -> None:
    """Plot the mesh with proper scaling."""
    collection = mplot3d.art3d.Poly3DCollection(to_plot, **kwargs)
    axes.add_collection3d(collection)
    plt.show()


def plot_points(points: np.ndarray,
                axes: Axes,
                **kwargs) -> None:
    """Plot the given points."""
    if points.ndim == 1:
        points = np.expand_dims(points, 0)
    axes.scatter(points[:, 0], points[:, 1], points[:, 2], **kwargs)
    plt.show()


def plot_lines(points: np.ndarray,
               axes: Axes,
               **kwargs) -> None:
    """Plot the given points."""
    axes.plot(points[:, 0], points[:, 1], points[:, 2], **kwargs)
    plt.show()


def equal_scale(truc: mesh.Mesh, axes: Axes) -> None:
    """Revert back to equal scaling."""
    scale = truc.points.flatten()
    axes.auto_scale_xyz(scale, scale, scale)
    plt.show()


# =============================================================================
# Try something
# =============================================================================
def ray_triangle_intersection(ray_near: np.ndarray,
                              ray_dir: np.ndarray,
                              v123: tuple[float, float, float],
                              eps: float = 0.000001,
                              ) -> tuple[bool, np.ndarray | None]:
    """
    Determine if ``ray_near`` intersects the cell.

    Based on Möller–Trumbore intersection algorithm.
    Based on http://en.wikipedia.org/wiki/M%C3%B6ller%E2%80%93Trumbore_intersection_algorithm
    Stolen from ``printrun``: https://github.com/kliment/Printrun/blob/master/printrun/stltool.py#L47

    Parameters
    ----------
    ray_near : np.ndarrray
        (3) array containing the coordinates of the ray origin.
    ray_dir : np.ndarray
        (3) array containing the direction of the ray.
    v123 : tuple[np.ndarray, np.ndarray, np.ndarray]
        Three points defining the triangular edge.
    eps : float
        Tolerance, optional. The default is 0.000001.

    Returns
    -------
    bool
        If there is an intersection between the ray and the edge.
    t : np.ndarray | None
        Position of the intersection if there is one.
        Or distance from the ray's origin to the intersectionP.

    """
    v1, v2, v3 = v123
    edge1 = v2 - v1
    edge2 = v3 - v1

    cross_product = np.cross(ray_dir, edge2)
    det = edge1.dot(cross_product)

    if abs(det) < eps:
        # Ray parallel to triangle
        return False, None

    inv_det = 1. / det
    tvec = ray_near - v1
    u = tvec.dot(cross_product) * inv_det
    if u < 0. or u > 1.:
        return False, None

    qvec = np.cross(tvec, edge1)
    v = ray_dir.dot(qvec) * inv_det
    if v < 0. or u + v > 1.:
        return False, None

    # At this point we can compute t to find out where the intersection point
    # is on the line
    t = edge2.dot(qvec) * inv_det

    # Line intersection but no ray intersection
    if t < eps:
        return False, None

    return True, t


def ray_mesh_intersections(ray_near: np.ndarray,
                           ray_dir: np.ndarray,
                           truc: mesh.Mesh
                           ) -> tuple[list[bool], list[float | None]]:
    """Get all intersections between ray and complete mesh."""
    collisions, distances = [], []
    for cell in truc.vectors:
        v123 = (cell[:, 0], cell[:, 1], cell[:, 2])
        collision, distance = ray_triangle_intersection(ray_near,
                                                        ray_dir,
                                                        v123)
        collisions.append(collision), distances.append(distance)
    return collisions, distances

# my_mesh = mesh.Mesh.from_file('tesla.stl')

# fig = plt.figure()
# axes = fig.add_subplot(projection='3d')
# axes.add_collection3d(mplot3d.art3d.Poly3DCollection(my_mesh.vectors))

# scale = my_mesh.points.flatten()
# axes.auto_scale_xyz(scale, scale, scale)
# plt.show()


if __name__ == '__main__':
    fig, axes = create_3d_fig()

    data = generate_data_for_half_cube()
    cube = half_cube_data_to_cube(data)
    plot_mesh(cube.vectors, axes, **{'edgecolors': 'k',
                                     'facecolors': 'g',
                                     'alpha': .5,
                                     })

    trajectory = generate_linear_trajectory(np.array([0., 0., 0.]),
                                            np.array([0.7, -0.32, 0.4]))
    plot_lines(trajectory, axes, **{'c': 'r'})

    # min_distance, cell_idx, time_idx = get_collision(trajectory, cube)
    # plot_points(centroids[cell_idx], axes, **{'c': 'k', 's': 100})
    # plot_points(trajectory[time_idx], axes, **{'c': 'k', 's': 100})

    ray_near = trajectory[0]
    ray_dir = trajectory[-1] - trajectory[0]
    collisions, distances = ray_mesh_intersections(ray_near, ray_dir, cube)

    impacted_cells = cube.vectors[collisions]
    plot_mesh(impacted_cells, axes, **{'facecolors': 'b',
                                       'alpha': 0.8,
                                       })

    equal_scale(cube, axes)
