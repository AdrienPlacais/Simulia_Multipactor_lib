#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 09:23:41 2023.

@author: placais
"""
import os
import random as rand
import numpy as np
import matplotlib.pyplot as plt

from palettable.colorbrewer.qualitative import Dark2_8
from cycler import cycler

import multipactor.loaders.loader_spark as lspark
import multipactor.visualization.plot as mp_plt
import multipactor.util.exp_growth as mp_exp

font = {'family': 'serif',
        'size': 25}
plt.rc('font', **font)
plt.rcParams['axes.prop_cycle'] = cycler(color=Dark2_8.mpl_colors)


# =============================================================================
# Parameters
# =============================================================================
# What you want to save
savefigs = False
savedat = False

# What you want to plot
plot_some_pop_evolutions = True
plot_exp_growth_factors = True
print_fit_parameters = False

# =============================================================================
# Load data and associated parameter
# =============================================================================
freq = 1.30145
period = 1. / freq
omega_0 = 2. * np.pi * freq
fitting_range = 20. * period

# Load file
base = "spark"

e_acc = np.linspace(1e6, 3e7, 30)
filepath = os.path.join(base, "time_results.csv")
label = "csv (manual export)"

# e_acc = np.linspace(1e6, 3e7, 291)
# filepath = os.path.join(base, "time_results.txt")
# label = "txt (batch auto export)"

# Different loading functions for txt or csv
d_get_pop = {".csv": lspark.get_population_evolution,
             ".txt": lspark.get_time_results}
filetype = os.path.splitext(filepath)[-1]
get = d_get_pop[filetype]

# Load data
d_data, parameters = get(filepath, e_acc=e_acc)

del filetype, d_get_pop, get
# =============================================================================
# FIXME portions that could be simplified but are kept for consistency with CST
# =============================================================================
# Map dic entry to accelerating field value
map_id = {1 + i: e_acc[i] for i in range(len(e_acc))}

key_part = 'Particle vs. Time'
key_model = key_part + ' (model)'
key_alfa = 'alfa (model)'
key_eacc = 'E_acc in MV per m'

# =============================================================================
# Exp growth fit
# =============================================================================
mp_exp.fit_all_spark(str_model='classic', d_data=d_data, key_part=key_part,
                     fitting_range=fitting_range)

# =============================================================================
# Plot some data
# =============================================================================
if plot_some_pop_evolutions:
    # Plot five Electrons vs Time maximum
    n_plots = min(5, len(e_acc))

    d_data_sample = {}
    map_id_sample = {}
    for i in rand.sample(list(d_data.keys()), n_plots):
        d_data_sample[i] = d_data[i]
        map_id_sample[i] = map_id[i]

    kwargs = {'x_label': "Time [ns]", 'y_label': "Electrons", 'yscale': 'log',
              'title': f'Labels correspond to: {None}'}
    _, axx = mp_plt.plot_dict_of_arrays(d_data_sample, map_id_sample, key_part,
                                        **kwargs)
    # We want to plot the modelled exp growth with dashed thicker line and the
    # same color as the reference
    lines = axx.get_lines()
    l_plot_kwargs = [{'ls': '--',
                      'lw': 4,
                      'c': line.get_color()
                      } for line in lines]
    _, _ = mp_plt.plot_dict_of_arrays(d_data_sample, map_id_sample, key_model,
                                      **kwargs, l_plot_kwargs=l_plot_kwargs)


# =============================================================================
# Plot the exponential growth factors
# =============================================================================
if plot_exp_growth_factors:
    keys_param_alfa = (key_eacc, )
    fig, ax = mp_plt.create_fig_if_not_exists(1, num=2)
    ax = ax[0]
    alfas = [d_data[i + 1][key_alfa] for i in range(len(e_acc))]
    ax.plot(e_acc, alfas, label=label)
    ax.grid(True)
    ax.set_xlabel(r"$E_{acc}$ [MV/m]")
    ax.set_ylabel(r"$\alpha$ [1/ns]")
    ax.legend()

    if savedat:
        save_me = np.column_stack((e_acc, alfas))
        np.savetxt(os.path.join(base, '../exp_growth.txt'), save_me)
