#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Define functions to study collisions with a ``Mesh`` from ``stl`` package.

For that we use the Möller–Trumbore intersection algorithm.

.. warning::
    Not maintained anymore. Prefer the ``vedo`` version. Keep it for legacy.

"""
import numpy as np
import stl

from multipactor.particle_monitor.collisions.util import (
    triangles_ray_intersections,
)


def part_mesh_intersections(
        origins: np.ndarray,
        directions: np.ndarray,
        structure: stl.mesh.Mesh,
        eps: float = 1e-6,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Get all intersections between particles and complete mesh.

    .. todo::
        explain why so many particles do not find their collision vertice

    Parameters
    ----------
    origins : np.ndarray(n, 3)
        Holds the origins of the ``n`` particles.
    directions : np.ndarray(n, 3)
        Holds the directions of the ``n`` particles.
    structure : stl.mesh.Mesh
        An object with ``m`` triangular cells.
    eps : float, optional
        Tolerance, optional. The default is 1e-6.

    Returns
    -------
    all_collisions : np.ndarray[bool](n, m)
        Indicates where there was collisions.
    all_distances : np.ndarray(n, m)
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

    args = (m_mesh, edges_1, edges_2, vertices_1, structure.normals, eps)

    for i, (origin, direction) in enumerate(zip(origins, directions)):
        collisions, distances, impact_angles = triangles_ray_intersections(
            origin, direction, *args)

        all_collisions[i] = collisions
        all_distances[i] = distances
        all_impact_angles[i] = impact_angles

    return all_collisions, all_distances, all_impact_angles
