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


def part_mesh_intersections(
        origins: np.ndarray,
        directions: np.ndarray,
        structure: mesh.Mesh,
        eps: float = 1e-6,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Get all intersections between particles and complete mesh.

    Based on `Möller–Trumbore intersection algorithm`_. Stolen and adapted from
    `printrun`_ library. Parallel implementation taken from `@V0XNIHILI`_.

    .. _Möller–Trumbore intersection algorithm: http://en.wikipedia.org/wiki/\
M%C3%B6ller%E2%80%93Trumbore_intersection_algorithm
    .. _printrun: https://github.com/kliment/Printrun/blob/master/printrun/\
stltool.py#L47
    .. _@V0XNIHILI: https://gist.github.com/V0XNIHILI/\
87c986441d8debc9cd0e9396580e85f4

    .. todo::
        explain why so many particles do not find their collision vertice

    Parameters
    ----------
    origins : np.ndarray(n, 3)
        Holds the origins of the ``n`` particles.
    directions : np.ndarray(n, 3)
        Holds the directions of the ``n`` particles.
    structure : mesh.Mesh
        An object with ``m`` triangular cells.
    eps : float, optional
        Tolerance, optional. The default is 1e-6.

    Returns
    -------
    collisions : np.ndarray[bool](n, m)
        Indicates where there was collisions.
    distances_to_collision : np.ndarray(n, m)
        Indicates distances between collisions and ``origins``.
    impact_angles : np.ndarray(n, m)
        Impact angle of every particle with every mesh cell (is np.NaN if there
        was no collision).

    """
    vertices_1 = structure.v0
    vertices_2 = structure.v1
    vertices_3 = structure.v2

    n_part = len(origins)
    m_mesh = len(vertices_1)
    output_shape = (n_part, m_mesh)

    all_collisions = np.full(output_shape, True)
    all_distances = np.zeros(output_shape)
    all_impact_angles = np.full(output_shape, np.NaN)

    # Shape (m, 3)
    edges_1 = vertices_2 - vertices_1
    edges_2 = vertices_3 - vertices_1

    for i, (orig, direction) in enumerate(zip(origins, directions)):
        # (m,)
        collisions = np.full((m_mesh), True)
        distances = np.zeros((m_mesh))
        impact_angles = np.full((m_mesh), np.NaN)

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

        distances[collisions] = distance[collisions]

        all_collisions[i] = collisions
        all_distances[i] = distances

        # To compute angle
        adjacents = structure.normals[collisions].dot(direction)
        opposites = np.linalg.norm(np.cross(structure.normals[collisions],
                                            direction))
        tan_theta = opposites / adjacents
        impact_angles[collisions] = np.abs(np.arctan(tan_theta))

        all_impact_angles[i] = impact_angles

    return all_collisions, all_distances, all_impact_angles
