#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 13:14:58 2023

@author: placais
"""

import numpy as np
import matplotlib.pyplot as plt
# from collections import OrderedDict

from palettable.colorbrewer.qualitative import Dark2_8
from cycler import cycler

font = {'family': 'serif', 'size': 25}
plt.rc('font', **font)
plt.rcParams['axes.prop_cycle'] = cycler(color=Dark2_8.mpl_colors)
plt.rcParams["figure.figsize"] = (19.2, 11.24)
plt.rcParams["figure.dpi"] = 100


def plot_dict_of_arrays(d_data: dict, map_id: dict, key_data: str, **kwargs):
    """
    Plot 2D data for every set of parameters.

    Parameters
    ----------
    d_data : dict
        Data as returned by loader_cst.get_parameter_sweep_auto_export.
    map_id : dict
        Links every d_data key to parameter values, as returned by
        loader_cst.full_map_param_to_id.
    key_data : str
        Key to the 2D data that you want to plot.
    x_label : str, optional
        x label. The default is None.
    y_label : str, optional
        y label. The default is None.
    labels : dict, optional
        Dict of strings for every parameter. The default is None.

    Returns
    -------
    fig : matplotlib.figure.Figure
        Figure plotted.
    axx : matplotlib.axes.Axes
        Plotted axe.

    """
    fig, axx = create_fig_if_not_exists(1, sharex=True)
    if 'x_label' in kwargs.keys():
        axx[-1].set_xlabel(kwargs['x_label'])

    axx = axx[0]
    if 'y_label' in kwargs.keys():
        axx.set_ylabel(kwargs['y_label'])
    axx.grid(True)

    if 'yscale' in kwargs.keys():
        axx.set_yscale(kwargs['yscale'])

    if 'title' in kwargs.keys():
        axx.set_title(kwargs['title'], {'fontsize': 10})

    for _id, val in map_id.items():
        axx.plot(d_data[_id][key_data][:, 0], d_data[_id][key_data][:, 1],
                 label=val)
    axx.legend()

    return fig, axx


# =============================================================================
# Generic plot helpers
# =============================================================================
def create_fig_if_not_exists(axnum, sharex=False, num=1, clean_fig=False):
    """
    Check if figures were already created, create it if not.

    Parameters
    ----------
    axnum : list of int or int
        Axes indexes as understood by fig.add_subplot or number of desired
        axes.
    sharex : boolean, opt
        If x axis should be shared.
    num : int, opt
        Fig number.
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

    fig = plt.figure(num)
    axlist = []
    axlist.append(fig.add_subplot(axnum[0]))

    d_sharex = {True: axlist[0], False: None}

    for i in axnum[1:]:
        axlist.append(fig.add_subplot(i, sharex=d_sharex[sharex]))
    return fig, axlist


def _clean_fig(fignumlist):
    """Clean axis of Figs in fignumlist."""
    for fignum in fignumlist:
        fig = plt.figure(fignum)
        for axx in fig.get_axes():
            axx.cla()


def _savefig(fig, filepath):
    """Saves the figure."""
    # fig.tight_layout()
    fig.savefig(filepath)
    print(f"plot._savefig info: Fig. saved in {filepath}")
