#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Define functions to study collisions with a ``Mesh`` from ``vedo`` package.

For that we use the ``vedo`` built-in methods.

"""
import numpy as np
import vedo


def part_mesh_intersections(
    origin_segment: np.ndarray,
    end_segment: np.ndarray,
    structure: vedo.Mesh,
    eps: float = 1e-6,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Get all intersections between particles and complete mesh.

    Parameters
    ----------
    structure : vedo.Mesh
        An object with triangular cells.
    eps : float, optional
        Tolerance, optional. The default is 1e-6.

    Returns
    -------
    all_collisions : np.ndarray[bool](n, m)
        Indicates where there was collisions.
    all_distances : np.ndarray(n, m)
        Indicates distances between collisions and ``origins``.
    impact_angles : np.ndarray(n, m)
        Impact angle of every particle with every mesh cell (is np.nan if there
        was no collision).

    """
    pass
