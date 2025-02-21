"""Define basic functions to treat data from :class:`.ParticleMonitor` object.

In particular, plotthe emission energy, the collision energy or the
trajectories of the particles.

"""

from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from simultipac.particle_monitor.collisions.vedo_mesh_collisions import (
    part_mesh_intersections,
)
from simultipac.particle_monitor.particle_monitor import ParticleMonitor


def plot_emission_energies(
    particles: ParticleMonitor,
    bins: int = 1000,
    hist_range: tuple[float, float] = (0.0, 1e4),
) -> Figure:
    """
    Plot the emission energies sorted by source id as a histogram.

    Parameters
    ----------
    particles : ParticleMonitor
        Object holding particles under study.
    bins : int, optional
        Number of bins in the histogram. The default is 1000.
    hist_range : tuple[float, float], optional
        Holds first and last energies of the histogram. The default is
        ``(0., 1e4)``.

    Returns
    -------
    fig : Figure
        The figure that was created.

    """
    fig, axes = create_fig_if_not_exists(2, sharex=True, num=1)
    axes[1].set_xlabel("Emission energy [eV]")
    axes[0].set_ylabel("Seed electrons")
    axes[1].set_ylabel("Emitted electrons")

    for i in range(2):
        emission_energies = particles.emission_energies(
            source_id=i, to_numpy=True
        )
        counts, bins = np.histogram(
            emission_energies, bins=bins, range=hist_range
        )
        axes[i].hist(bins[:-1], bins, weights=counts)
        axes[i].grid(True)
    return fig


def plot_collision_energies(
    particles: ParticleMonitor,
    bins: int = 1000,
    hist_range: tuple[float, float] = (0.0, 1e4),
) -> Figure:
    """
    Plot all the collision energies as histogram.

    Parameters
    ----------
    particles : ParticleMonitor
        Object holding particles under study.
    bins : int, optional
        Number of bins in the histogram. The default is 1000.
    hist_range : tuple[float, float], optional
        Holds first and last energies of the histogram. The default is
        ``(0., 1e4)``.

    Returns
    -------
    fig : Figure
        The figure that was created.

    """
    fig, axes = create_fig_if_not_exists(1, sharex=True, num=2)
    axes[0].set_xlabel("Collision energy [eV]")
    axes[0].set_ylabel("All electrons")

    collision_energies = particles.collision_energies(
        to_numpy=True, extrapolation=False, remove_alive_at_end=True
    )

    counts, bins = np.histogram(
        collision_energies, bins=bins, range=hist_range
    )
    axes[0].hist(bins[:-1], bins, weights=counts)
    axes[0].grid(True)
    return fig


def plot_collision_angles(
    particle_monitor: ParticleMonitor,
    bins: int = 100,
    hist_range: tuple[float, float] = (0.0, 90.0),
    **kwargs,
) -> Figure:
    """Compute and plot a particles impact angle histogram.

    Parameters
    ----------
    particles : ParticleMonitor
        particles
    bins : int
        bins
    hist_range : tuple[float, float]
        hist_range
    check_collisions : bool, optional
        Check how many particles intersected the mesh, and how many particles
        intersected the mesh several times. The default is False.

    Returns
    -------
    Figure

    """
    fig, axes = create_fig_if_not_exists(1, num=3, clean_fig=True)
    axes[0].set_xlabel(r"Impact angle $\theta$ [deg]")
    axes[0].set_ylabel("Distribution all electrons")

    collision_angles = [
        particle.collision_angle for particle in particle_monitor.values()
    ]

    counts, bins = np.histogram(
        np.rad2deg(collision_angles), bins=bins, range=hist_range
    )
    axes[0].hist(bins[:-1], bins, weights=counts)
    axes[0].grid(True)
    return fig


# Do the same function but in 3D
def plot_trajectories(
    particles: ParticleMonitor, particle_id: list[int], mesh: Any = None
) -> Figure:
    """Plot trajectories of particles with the desired ``pid``.

    Parameters
    ----------
    particles : ParticleMonitor
        Object holding particles under study.
    particle_id : list[int]
        List holding the ``pid`` (Particle ID) of the electrons which
        trajectory should be plotted.
    mesh : Any, optional
        Object holding the borders of the geometry for better representation.
        The default is None.

    Returns
    -------
    fig : Figure
        The figure that was created.

    Raises
    ------
    NotImplementedError : ``mesh`` different from None is not supported.

    """
    fig, axes = create_fig_if_not_exists(range(221, 224), num=4)

    if mesh is not None:
        raise NotImplementedError("Plot of mesh not implemented yet.")

    particles_to_plot = {
        pid: part for pid, part in particles.items() if pid in particle_id
    }

    projections = {
        "xy": lambda pos: pos[:, :2],
        "yz": lambda pos: pos[:, 1:],
        "xz": lambda pos: pos[:, [0, 2]],
    }
    for i, (projection_name, projection) in enumerate(projections.items()):
        axes[i].set_xlabel(projection_name[0] + " [mm]")
        axes[i].set_ylabel(projection_name[1] + " [mm]")
        axes[i].set_aspect("equal", adjustable="box")

        for part in particles_to_plot.values():
            projected_pos = projection(part.pos)
            (line,) = axes[i].plot(
                projected_pos[:, 0], projected_pos[:, 1], marker="o"
            )

            if part.extrapolated_pos is not None:
                projected_pos = projection(part.extrapolated_pos)
                axes[i].plot(
                    projected_pos[:, 0],
                    projected_pos[:, 1],
                    ls="--",
                    c=line.get_color(),
                )
    return fig


def plot_impact_density_distribution(
    particles: ParticleMonitor, mesh: Any
) -> Figure:
    raise NotImplementedError
    fig, axes = create_fig_if_not_exists(
        1, num=5, **{"projection": "3d", "proj_type": "ortho"}
    )
    axes.set_xlabel(r"$x$")
    axes.set_ylabel(r"$y$")
    axes.set_zlabel(r"$z$")

    last_known_position = particles.last_known_position(
        to_numpy=True, remove_alive_at_end=True
    )
    last_known_direction = particles.last_known_direction(
        to_numpy=True, normalize=True, remove_alive_at_end=True
    )

    # collisions has shape (n, m)
    collisions, _, _ = part_mesh_intersections(
        origins=last_known_position, directions=last_known_direction, mesh=mesh
    )
    collisions_per_cell = collisions.sum(axis=0)
    collision_density = collisions_per_cell / mesh.areas
    collision_density /= np.max(collision_density)


def create_fig_if_not_exists(
    axnum: int | list[int],
    sharex: bool = False,
    num: int = 1,
    clean_fig: bool = False,
    **kwargs,
) -> tuple[Figure, list[Axes]]:
    """
    Check if figures were already created, create it if not.

    Parameters
    ----------
    axnum : int | list[int]
        Axes indexes as understood by :func:`fig.add_subplot` or number of
        desired axes.
    sharex : boolean, optional
        If x axis should be shared. The default is False.
    num : int, optional
        Fig number. The default is 1.
    clean_fig : bool, optional
        To tell if the Figure should be cleaned from previous plots. The
        default is False.
    **kwargs : dict
        Dict passed to :func:`add_subplot`.

    Return
    ------
    fig : Figure
        Figure holding axes.
    axlist : list[Axes]
        Axes of Figure.

    """
    if isinstance(axnum, int):
        # We make a one-column, axnum rows figure
        axnum = range(100 * axnum + 11, 101 * axnum + 11)

    if plt.fignum_exists(num):
        fig = plt.figure(num)
        axlist = fig.get_axes()

        if clean_fig:
            _clean_fig([num])
        return fig, axlist

    fig = plt.figure(num, **kwargs)
    axlist = []
    axlist.append(fig.add_subplot(axnum[0], **kwargs))

    d_sharex = {True: axlist[0], False: None}

    for i in axnum[1:]:
        axlist.append(fig.add_subplot(i, sharex=d_sharex[sharex], **kwargs))
    if sharex:
        for ax in axlist[:-1]:
            plt.setp(ax.get_xticklabels(), visible=False)
    return fig, axlist


def _clean_fig(fignumlist: list[int]) -> None:
    """Clean axis of Figs in fignumlist."""
    for fignum in fignumlist:
        fig = plt.figure(fignum)
        for axx in fig.get_axes():
            axx.cla()
