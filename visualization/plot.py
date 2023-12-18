#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 13:14:58 2023.

@author: placais

In this module we store some generic helper functions for plotting.

"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes._axes import Axes

import multipactor.loaders.loader_cst as lcst


def plot_dict_of_arrays(data: dict,
                        map_id: dict,
                        key_data: str,
                        title: str | None = None,
                        x_label: str | None = None,
                        y_label: str | None = None,
                        yscale: str | None = None,
                        l_plot_kwargs: dict | list[dict] | None = None
                        ) -> tuple[Figure, list[Axes]]:
    """
    Plot 2D data for every set of parameters.

    Parameters
    ----------
    data : dict
        Data as returned by loader_cst.get_parameter_sweep_auto_export.
    map_id : dict
        Links every data key to parameter values, as returned by
        loader_cst.full_map_param_to_id.
    key_data : str
        Key to the 2D data that you want to plot.
    title : str | None, optional
        Plot title. The default is None.
    x_label : str | None, optional
        x axis label. The default is None.
    y_label : str | None, optional
        y axis label. The default is None.
    yscale : str | None, optional
        Key for set_yscale method. The default is None.
    l_plot_kwargs : dict | list[dict] | None, optional
        kwargs for the ax.plot method.
        If it is a dict, the same kwargs are used for every plot.
        If it is a list of dicts, it's length must match the length of data
        and map_id.

    Returns
    -------
    fig : Figure
        Figure plotted.
    axx : list[Axes]
        Plotted ax.

    """
    fig, axx = create_fig_if_not_exists(1, sharex=True, num=1)
    if title is not None:
        axx[0].set_title(title, {'fontsize': 10})
    if x_label is not None:
        axx[-1].set_xlabel(x_label)

    axx = axx[0]
    if y_label is not None:
        axx.set_ylabel(y_label)
    axx.grid(True)

    if yscale is not None:
        axx.set_yscale(yscale)

    # No specific plot kwargs
    if l_plot_kwargs is None:
        l_plot_kwargs = [{} for _id in map_id.keys()]
    # All plots have same kwargs
    elif isinstance(l_plot_kwargs, dict):
        l_plot_kwargs = [l_plot_kwargs for _id in map_id.keys()]

    for (_id, val), kwargs in zip(map_id.items(), l_plot_kwargs):
        axx.plot(data[_id][key_data][:, 0], data[_id][key_data][:, 1],
                 label=val, **kwargs)
    axx.legend()

    return fig, axx


def plot_dict_of_floats(data: dict,
                        key_ydata: str,
                        *args,
                        title: str | None = None,
                        x_label: str | None = None,
                        y_label: str | None = None,
                        yscale: str | None = None,
                        save_data: bool = False,
                        save_path: str | None = None
                        ) -> tuple[Figure, list[Axes]]:
    """
    Plot ``key_ydata`` as a function of first arg, for every other args.
    """
    if len(args) > 2:
        raise NotImplementedError('Not implemented')

    fig, axx = create_fig_if_not_exists(1, sharex=True, num=2)
    if title is not None:
        axx[0].set_title(title, {'fontsize': 10})
    if x_label is not None:
        axx[-1].set_xlabel(x_label)

    axx = axx[0]
    if y_label is not None:
        axx.set_ylabel(y_label)
    axx.grid(True)

    if yscale is not None:
        axx.set_yscale(yscale)

    plot_data = lcst.get_values(data, key_ydata, *args, to_numpy=True,
                                ins_param=True)

    x_data = plot_data[1:, 0]   # first of args
    y_data = plot_data[1:, 1:]  # key_ydata
    z_data = plot_data[0, 1:]   # second of args
    for i in range(y_data.shape[1]):
        axx.plot(x_data, y_data[:, i], label=f"{z_data[i]}", marker='o')

        if save_data:
            assert save_path is not None
            save_me = np.column_stack((x_data, y_data[:, i]))
            np.savetxt(save_path + f"param={z_data[i]}.txt", save_me)
    axx.legend()

    return fig, axx


# =============================================================================
# Generic plot helpers
# =============================================================================
def create_fig_if_not_exists(axnum: int | list[int],
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


def _savefig(fig: Figure, filepath: str) -> None:
    """Save the figure."""
    # fig.tight_layout()
    fig.savefig(filepath)
    print(f"plot._savefig info: Fig. saved in {filepath}")
