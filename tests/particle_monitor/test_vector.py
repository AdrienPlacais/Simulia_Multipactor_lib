"""Define tests for :class:`.Vector`."""

from unittest.mock import MagicMock

import numpy as np
from numpy.testing import assert_array_almost_equal, assert_array_equal

from simultipac.particle_monitor.vector import Momentum, Position, Vector


def test_append() -> None:
    """Test basic appending."""
    vector = Vector()
    vector.append((1.0, 2.0, 3.0))
    assert_array_equal(vector.array, np.array([[1.0, 2.0, 3.0]]))


def test_reorder() -> None:
    """Test basic reordering."""
    x = [1.0, 3.0, 2.0, 4.0]
    y = [p * 2 for p in x]
    z = [p * 3 for p in x]
    vector = Vector(x, y, z)

    index = np.array([0, 2, 1, 3])
    vector.reorder(index)

    expected_x = np.linspace(1.0, 4.0, 4)
    expected = np.column_stack((expected_x, 2 * expected_x, 3 * expected_x))
    assert_array_equal(vector.array, expected)


def test_extrapolate_position(mocker: MagicMock) -> None:
    """Test extrapolation of position."""
    momentum = Momentum((np.nan, 1.0), (np.nan, 0.0), (np.nan, -1.0))
    position = Position((0.0,), (0.0,), (0.0,))
    desired_times = (1.0, 2.0, 3.0)

    mocker.patch(
        "simultipac.particle_monitor.vector.adim_momentum_to_speed_mm_per_ns",
        return_value=momentum.array[-1, :],
    )
    position.extrapolate(momentum, desired_times)

    expected = np.array(
        [
            [1.0, 0.0, -1.0],
            [2.0, 0.0, -2.0],
            [3.0, 0.0, -3.0],
        ]
    )
    assert_array_equal(position.extrapolated, expected)


def test_extrapolate_momentum() -> None:
    """Test extrapolation of momentum."""
    momentum = Momentum((0.0, 0.0, 0.0), (0.0, 1.0, 2.0), (1.0, 4.0, 9.0))
    known_times = np.array([1.0, 2.0, 3.0])
    desired_times = np.array([4.0, 5.0, 6.0])
    momentum.extrapolate(
        known_times, desired_times, poly_fit_deg=2, n_points=3
    )
    expected = np.array(
        [
            [0.0, 3.0, 16.0],
            [0.0, 4.0, 25.0],
            [0.0, 5.0, 36.0],
        ]
    )
    assert_array_almost_equal(momentum.extrapolated, expected)
