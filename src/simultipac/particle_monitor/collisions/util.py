"""Define functions to be used everywhere in the subpackage."""

import numpy as np


def triangles_ray_intersections(
    origin: np.ndarray,
    direction: np.ndarray,
    m_mesh: int,
    edges_1: np.ndarray,
    edges_2: np.ndarray,
    vertices_1: np.ndarray,
    normals: np.ndarray,
    eps: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Detect collision between a single ray and several triangles of mesh.

    Based on `Möller–Trumbore intersection algorithm`_. Stolen and adapted from
    `printrun`_ library. Parallel implementation taken from `@V0XNIHILI`_.

    .. _`Möller–Trumbore intersection algorithm`: https://en.wikipedia.org/wik\
i/M%C3%B6ller%E2%80%93Trumbore_intersection_algorithm
    .. _printrun: https://github.com/kliment/Printrun/blob/master/printrun/\
stltool.py#L47
    .. _@V0XNIHILI: https://gist.github.com/V0XNIHILI/\
87c986441d8debc9cd0e9396580e85f4

    Parameters
    ----------
    origin : np.ndarray(3, )
        Holds the starting point of the ray.
    direction : np.ndarray(3, )
        Holds the direction of the ray.
    m_mesh : int
        Number of triangles under study.
    edges_1 : np.ndarray(m_mesh, 3)
        The first edge of every triangle.
    edges_2 : np.ndarray(m_mesh, 3)
        The second edge of every triangle.
    vertices_1 : np.ndarray(m_mesh, 3)
        The junction point of ``edges_1`` and ``edges_2`` for every triangle.
    normals : np.ndarray(m_mesh, 3)
        Normal vector of every triangle.
    eps : float
        Tolerance.

    Returns
    -------
    collisions : np.ndarray(m_mesh, )
        Array of booleans telling if there was a collision or not.
    distances : np.ndarray(m_mesh, )
        Array of floats giving distance between ``origin`` and the triangle.
    impact_angles : np.ndarray(m_mesh, )
        Holds the impact angles in radians, or a nan.

    """
    collisions = np.full((m_mesh), True)
    distances = np.zeros(m_mesh)
    impact_angles = np.full((m_mesh), np.nan)

    # Check if intersection line/plane or if they are just parallel
    pvec = np.cross(direction, edges_2)
    triple_products = np.sum(edges_1 * pvec, axis=1)
    no_collision_idx = np.absolute(triple_products) < eps
    collisions[no_collision_idx] = False
    distances[no_collision_idx] = np.nan

    inv_triple_prod = 1.0 / triple_products

    # First axis: check if intersection triangle/line or just plane/line
    tvec = origin - vertices_1
    u_coord = np.sum(tvec * pvec, axis=1) * inv_triple_prod
    no_collision_idx = (u_coord < 0.0) + (u_coord > 1.0)
    collisions[no_collision_idx] = False
    distances[no_collision_idx] = np.nan

    # Second axis: check if intersection triangle/line or just plane/line
    qvec = np.cross(tvec, edges_1)
    v_coord = np.sum(direction * qvec, axis=1) * inv_triple_prod
    no_collision_idx = (v_coord < 0.0) + (u_coord + v_coord > 1.0)
    collisions[no_collision_idx] = False
    distances[no_collision_idx] = np.nan

    # Check if intersection triangle/trajectory or just triangle/line
    distance = np.sum(edges_2 * qvec, axis=1) * inv_triple_prod
    no_collision_idx = distance < eps
    collisions[no_collision_idx] = False
    distances[no_collision_idx] = np.nan

    distances[collisions] = distance[collisions]

    # To compute angle
    adjacents = normals[collisions].dot(direction)
    opposites = np.linalg.norm(np.cross(normals[collisions], direction))
    tan_theta = opposites / adjacents
    impact_angles[collisions] = np.abs(np.arctan(tan_theta))

    return collisions, distances, impact_angles
