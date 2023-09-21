#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 09:08:40 2023.

@author: placais

In this module we store functions to detect collisions between particles and
mesh.

"""
import numpy as np
from stl import mesh


def vectorized_part_mesh_intersections(
    part_origins: np.ndarray,
    part_directions: np.ndarray,
    truc: mesh.Mesh,
    max_distances: np.ndarray | None = None,
    eps: float = 1e-6,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Get all intersections between particles and complete mesh.

    Based on `Möller–Trumbore intersection algorithm`_. Stolen and adapted from
    `printrun`_ library. Parallel implementation taken from `@V0XNIHILI`_.
V0XNIHILI

    .. _Möller–Trumbore intersection algorithm: http://en.wikipedia.org/wiki/\
M%C3%B6ller%E2%80%93Trumbore_intersection_algorithm
    .. _printrun: https://github.com/kliment/Printrun/blob/master/printrun/\
stltool.py#L47
    .. _@V0XNIHILI: https://gist.github.com/V0XNIHILI/\
87c986441d8debc9cd0e9396580e85f4


    Parameters
    ----------
    part_origins : np.ndarray(n, 3)
        Holds the origins of the ``n`` particles.
    part_directions : np.ndarray(n, 3)
        Holds the directions of the ``n`` particles.
    truc : mesh.Mesh
        An object with ``m`` triangular cells.
    max_distances : np.ndarray(n)
        Max distance crossed by every particle.
    eps : float, optional
        Tolerance, optional. The default is 1e-6.

    Returns
    -------
    np.ndarray<bool>(n, m)
        Indicates where there was collisions.
    np.ndarray(n, m)
        Indicates distances between collisions and ``part_origins``.

    """
    vertices_1, vertices_2, vertices_3 = truc.v0, truc.v1, truc.v2

    n_part = len(part_origins)
    m_mesh = len(vertices_1)
    output_shape = (n_part, m_mesh)

    all_collisions = np.full(output_shape, True)
    all_distances = np.zeros(output_shape)

    # Shape (m, 3)
    edges_1 = vertices_2 - vertices_1
    edges_2 = vertices_3 - vertices_1

    for i, (orig, direction) in enumerate(zip(part_origins, part_directions)):
        # (m,)
        collisions = np.full((m_mesh), True)
        distances = np.zeros((m_mesh))
        # triple_products = edges_1.dot(normals)

        # Check if intersection line/plane or if they are just parallel
        pvec = np.cross(direction, edges_2)
        triple_products = np.sum(edges_1 * pvec, axis=1)
        no_collision_idx = np.absolute(triple_products) < eps
        collisions[no_collision_idx] = False
        distances[no_collision_idx] = np.NaN

        inv_triple_prod = 1.0 / triple_products

        # First axis: check if intersection triangle/line or just plane/line
        tvec = orig - vertices_1
        u_coord = np.sum(tvec * pvec, axis=1) * inv_triple_prod
        no_collision_idx = (u_coord < 0.0) + (u_coord > 1.0)
        collisions[no_collision_idx] = False
        distances[no_collision_idx] = np.NaN

        # Second axis: check if intersection triangle/line or just plane/line
        qvec = np.cross(tvec, edges_1)
        v_coord = np.sum(direction * qvec, axis=1) * inv_triple_prod
        no_collision_idx = (v_coord < 0.0) + (u_coord + v_coord > 1.0)
        collisions[no_collision_idx] = False
        distances[no_collision_idx] = np.NaN

        # Check if intersection triangle/trajectory or just triangle/line
        distance = np.sum(edges_2 * qvec, axis=1) * inv_triple_prod
        no_collision_idx = distance < eps
        collisions[no_collision_idx] = False
        distances[no_collision_idx] = np.NaN

        collision_idx = np.invert(no_collision_idx)
        distances[collision_idx] = distance[collision_idx]

        all_collisions[i] = collisions
        all_distances[i] = distances

    return all_collisions, all_distances


# =============================================================================
# Legacy
# =============================================================================
def _ray_triangle_intersection(
    ray_origin: np.ndarray,
    ray_direction: np.ndarray,
    vertex_1: np.ndarray,
    vertex_2: np.ndarray,
    vertex_3: np.ndarray,
    eps: float = 1e-6,
    max_distance: float = 1.0,
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
    inv_triple_product = 1.0 / triple_product
    tvec = ray_origin - vertex_1
    u_coord = tvec.dot(cell_normal) * inv_triple_product

    if u_coord < 0.0 or u_coord > 1.0:
        # Intersection point is in the plane but not in the triangle

        return False, None

    qvec = np.cross(tvec, edge_1)
    v_coord = ray_direction.dot(qvec) * inv_triple_product

    if v_coord < 0.0 or u_coord + v_coord > 1.0:
        # Intersection point is in the plane but not in the triangle

        return False, None

    t_coord = edge_2.dot(qvec) * inv_triple_product

    if t_coord < eps or t_coord > max_distance:
        # Line intersection but no ray intersection

        return False, None

    return True, t_coord


def ray_mesh_intersections(
    ray_origin: np.ndarray,
    ray_direction: np.ndarray,
    truc: mesh.Mesh,
    max_distance: float,
) -> tuple[list[bool], list[float | None]]:
    """Get all intersections between ray and complete mesh."""
    collisions, distances = [], []

    for cell_v0, cell_v1, cell_v2 in zip(truc.v0, truc.v1, truc.v2):
        collision, distance = _ray_triangle_intersection(
            ray_origin,
            ray_direction,
            cell_v0,
            cell_v1,
            cell_v2,
            max_distance=max_distance,
        )
        collisions.append(collision)
        distances.append(distance)

    return collisions, distances
