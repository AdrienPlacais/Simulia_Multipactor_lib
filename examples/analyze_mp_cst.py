#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 09:23:41 2023.

@author: placais

This script showcases how CST data can be analyzed. Data must comes from the
``Export Parametric`` option of CST.

"""
import os.path
import random as rand
import numpy as np
import matplotlib.pyplot as plt

from palettable.colorbrewer.qualitative import Dark2_8
from cycler import cycler

import multipactor.loaders.loader_cst as lcst
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
plot_some_pop_evolutions = False
plot_exp_growth_factors = True
print_fit_parameters = False

# =============================================================================
# Load data and associated parameter
# =============================================================================
material = 'baked'
# In Parameters.txt
key_eacc = 'E_acc'
key_size_cell = 'size_cell'
key_freq = 'f'
key_npart = 'N_0'


filepath = "cst/Export_Parametric"
keys_param = (key_eacc, key_npart, key_freq)

# Files created by CST
key_part = 'Particle vs. Time'
# Created by user
key_alfa = 'alfa (model)'
key_model = f"{key_part} (model)"

key_to_markdown_label = {key_eacc: r"$E_{acc}$ [V/m]",
                         key_size_cell: "Max. size of meshcell [mm]",
                         key_freq: "Frequency [GHz]",
                         key_alfa: r"$\alpha$ [1/ns]",
                         key_npart: r"Init. number of electrons"
                         }

labels = [key_to_markdown_label[key] for key in keys_param]

# Load all data from all simulations
data = lcst.get_parameter_sweep_auto_export(filepath)
for key in data.keys():
    data[key]['Parameters']['N_0'] = np.round(data[key]['Parameters']['N_0'],
                                              0)

# Parameters we are interested into
map_id, d_uniques = lcst.full_map_param_to_id(data, *keys_param)
if len(d_uniques[key_freq]) != 1:
    print(f"""analyze_mp warning: more than one frequency detected.
          Only considering f={d_uniques[key_freq][0]}""")

# Should be in GHz, watch out!
freq = d_uniques[key_freq][0] * 1e-9
period = 1. / freq
omega_0 = 2. * np.pi * freq
fitting_range = 5. * period

# =============================================================================
# Exp growth fit
# =============================================================================
mp_exp.fit_all(str_model='classic', data=data, map_id=map_id,
               key_part=key_part, period=period, fitting_range=fitting_range)

# =============================================================================
# Plot some data
# =============================================================================
if plot_some_pop_evolutions:
    # Plot five Electrons vs Time maximum
    n_plots = min(5, len(map_id))

    data_sample = {}
    map_id_sample = {}
    for i in rand.sample(list(map_id.keys()), n_plots):
        data_sample[i] = data[i]
        map_id_sample[i] = map_id[i]

    kwargs = {'x_label': "Time [ns]", 'y_label': "Electrons", 'yscale': 'log',
              'title': f'Labels correspond to: {labels}'}
    _, axx = mp_plt.plot_dict_of_arrays(data_sample, map_id_sample, key_part,
                                        **kwargs)
    # We want to plot the modelled exp growth with dashed thicker line and the
    # same color as the reference
    lines = axx.get_lines()
    l_plot_kwargs = [{'ls': '--',
                      'lw': 4,
                      'c': line.get_color()
                      } for line in lines]
    _, _ = mp_plt.plot_dict_of_arrays(data_sample, map_id_sample, key_model,
                                      **kwargs, l_plot_kwargs=l_plot_kwargs)


# =============================================================================
# Plot the exponential growth factors
# =============================================================================
if plot_exp_growth_factors:
    keys_param = (key_eacc, key_npart)

    labels = [key_to_markdown_label[key] for key in keys_param]
    kwargs = {
        'x_label': key_to_markdown_label[key_eacc],
        'y_label': key_to_markdown_label[key_alfa],
        }
    save_path = os.path.join(filepath, '../savedata',
                             f'exp_growth_{material}_sizecell_')

    _, _ = mp_plt.plot_dict_of_floats(data, key_alfa, *keys_param,
                                      save_data=savedat, save_path=save_path)
