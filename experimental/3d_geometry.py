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
# Plotting
# =============================================================================
def create_3d_fig() -> tuple[Figure, Axes]:
    """Create the 3d plot."""
    fig = plt.figure(1)
    axes = fig.add_subplot(projection='3d')
    axes.set_xlabel(r"$x$")
    axes.set_ylabel(r"$y$")
    axes.set_zlabel(r"$z$")
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
# Collision detection
# =============================================================================
def generate_random_ray(truc: mesh.Mesh,
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
        max_distance = .8 * (np.mean(max_) - np.mean(min_))
    trajectory = np.vstack((ray_origin,
                            ray_origin + max_distance * ray_direction))
    return ray_origin, ray_direction, trajectory, max_distance


def ray_triangle_intersection(ray_origin: np.ndarray,
                              ray_direction: np.ndarray,
                              vertex_1: np.ndarray,
                              vertex_2: np.ndarray,
                              vertex_3: np.ndarray,
                              eps: float = 1e-6,
                              max_distance: float = 1.,
                              ) -> tuple[bool, np.ndarray | None]:
    """
    Determine if ``ray_origin`` intersects the cell.

    Based on `Möller–Trumbore intersection algorithm`_. Stolen and adapted from
    `printrun`_ library.

    .. _Möller–Trumbore intersection algorithm: http://en.wikipedia.org/wiki/\
M%C3%B6ller%E2%80%93Trumbore_intersection_algorithm
    .. _printrun: https://github.com/kliment/Printrun/blob/master/printrun/\
stltool.py#L47

    Parameters
    ----------
    ray_origin : (3,) np.ndarrray
        Contains the coordinates of the ray origin.
    ray_direction : (3,) np.ndarray
        Contains the direction of the ray.
    vertex_1, vertex_2, vertex_3 : np.ndarray
        Three vertices of the triangular mesh cell.
    eps : float
        Tolerance, optional. The default is 1e-6.

    Returns
    -------
    bool
        If there is an intersection between the ray and the edge.
    t_coord : np.ndarray | None
        Distance from the ray's origin to the intersection point.

    """
    edge_1 = vertex_2 - vertex_1
    edge_2 = vertex_3 - vertex_1

    cell_normal = np.cross(ray_direction, edge_2)
    triple_product = edge_1.dot(cell_normal)

    if abs(triple_product) < eps:
        # Ray parallel to triangle plane
        return False, None

    # We are looking for u_coord and v_coord (u and v in Wikipedia), the
    # coordinates of the ray intersection with the plane of the triangle
    inv_triple_product = 1. / triple_product
    tvec = ray_origin - vertex_1
    u_coord = tvec.dot(cell_normal) * inv_triple_product
    if u_coord < 0. or u_coord > 1.:
        # Intersection point is in the plane but not in the triangle
        return False, None

    qvec = np.cross(tvec, edge_1)
    v_coord = ray_direction.dot(qvec) * inv_triple_product
    if v_coord < 0. or u_coord + v_coord > 1.:
        # Intersection point is in the plane but not in the triangle
        return False, None

    t_coord = edge_2.dot(qvec) * inv_triple_product
    if t_coord < eps or t_coord > max_distance:
        # Line intersection but no ray intersection
        return False, None

    return True, t_coord


def ray_mesh_intersections(ray_origin: np.ndarray,
                           ray_direction: np.ndarray,
                           truc: mesh.Mesh,
                           max_distance: float,
                           ) -> tuple[list[bool], list[float | None]]:
    """Get all intersections between ray and complete mesh."""
    collisions, distances = [], []
    for cell_v0, cell_v1, cell_v2 in zip(truc.v0, truc.v1, truc.v2):
        collision, distance = ray_triangle_intersection(
            ray_origin,
            ray_direction,
            cell_v0,
            cell_v1,
            cell_v2,
            max_distance=max_distance,
        )
        collisions.append(collision), distances.append(distance)
    return collisions, distances


if __name__ == '__main__':
    debug = True
    fig, axes = create_3d_fig()

    data = generate_data_for_half_cube()
    cube = half_cube_data_to_cube(data)
    my_mesh = cube

    if not debug:
        my_mesh = mesh.Mesh.from_file('tesla.stl')

    plot_mesh(my_mesh.vectors, axes, **{'edgecolors': 'k',
                                        'linewidths': 0.1,
                                        'facecolors': 'g',
                                        'alpha': .3,
                                        })

    ray_origin, ray_direction, trajectory, max_distance = generate_random_ray(
        my_mesh, seed=None)
    plot_lines(trajectory, axes, **{'c': 'r'})
    plot_points(trajectory, axes, **{'c': 'r', 's': 50})

    collisions, distances = ray_mesh_intersections(ray_origin,
                                                   ray_direction,
                                                   my_mesh,
                                                   max_distance)

    impacted_cells = my_mesh.vectors[collisions]
    print(f"Number of impacted cells: {len(impacted_cells)}")
    plot_mesh(impacted_cells, axes, **{'facecolors': 'b',
                                       'edgecolors': 'k',
                                       'alpha': 0.7,
                                       })

    if len(impacted_cells) > 0:
        impact_points = np.array([ray_origin + distance * ray_direction
                                  for distance in distances
                                  if distance is not None])
        plot_points(impact_points, axes, **{'c': 'k',
                                            's': 100,
                                            'marker': 's'})

    equal_scale(my_mesh, axes)
