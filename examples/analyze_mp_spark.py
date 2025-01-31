#!/usr/bin/env python3
"""Showcase how multipactor can be analyzed from SPARK3D files.

For files manually exported (Right-click on ``Multipactor results``,
``Export to CSV``), use :func:`get_population_evolution``.
For files automatically exported by SPARK3D, use :func:`get_time_results`.

.. todo::
    Should be more user-friendly.

.. todo::
    xlabel is wrong

"""
import random as rand
from pathlib import Path

import numpy as np

import simultipac.loaders.loader_spark as lspark
import simultipac.util.exp_growth as mp_exp
import simultipac.visualization.plot as mp_plt

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
period = 1.0 / freq
omega_0 = 2.0 * np.pi * freq
fitting_range = 20.0 * period

basefolder = Path("spark")

e_acc = np.linspace(1e6, 3e7, 30)
filepath = Path(basefolder, "time_results.csv")
label = "csv (manual export)"

# e_acc = np.linspace(1e6, 3e7, 291)
# filepath = Path(basefolder, "time_results.txt")
# label = "txt (batch auto export)"

key_part = "Particle vs. Time"
key_eacc = "E_acc in MV per m"
key_power = "power_rms"

complete_population_evolutions, parameters = lspark.load_population_evolution(
    filepath, e_acc, key_part=key_part, key_eacc=key_eacc, key_power=key_power
)

# =============================================================================
# FIXME portions that could be simplified but are kept for consistency with CST
# =============================================================================
# Map dic entry to accelerating field value
map_id = {1 + i: e_acc[i] for i in range(len(e_acc))}

key_model = key_part + " (model)"
key_alfa = "alfa (model)"

# =============================================================================
# Exp growth fit
# =============================================================================
mp_exp.fit_all_spark(
    "classic",
    complete_population_evolutions,
    key_eacc=key_eacc,
    key_part=key_part,
    period=period,
    fitting_range=fitting_range,
)

# =============================================================================
# Plot some data
# =============================================================================
if plot_some_pop_evolutions:
    # Plot five Electrons vs Time maximum
    n_plots = min(5, len(e_acc))

    data_sample = {}
    map_id_sample = {}
    for i in rand.sample(list(complete_population_evolutions.keys()), n_plots):
        data_sample[i] = complete_population_evolutions[i]
        map_id_sample[i] = map_id[i]

    kwargs = {
        "x_label": "Time [ns]",
        "y_label": "Electrons",
        "yscale": "log",
        "title": f"Labels correspond to: {None}",
    }
    _, axx = mp_plt.plot_dict_of_arrays(
        data_sample, map_id_sample, key_part, **kwargs
    )
    # We want to plot the modelled exp growth with dashed thicker line and the
    # same color as the reference
    lines = axx.get_lines()
    l_plot_kwargs = [
        {"ls": "--", "lw": 4, "c": line.get_color()} for line in lines
    ]
    _, _ = mp_plt.plot_dict_of_arrays(
        data_sample,
        map_id_sample,
        key_model,
        **kwargs,
        l_plot_kwargs=l_plot_kwargs,
    )


# =============================================================================
# Plot the exponential growth factors
# =============================================================================
if plot_exp_growth_factors:
    keys_param_alfa = (key_eacc,)
    fig, ax = mp_plt.create_fig_if_not_exists(1, num=2)
    ax = ax[0]
    alfas = [
        complete_population_evolutions[i + 1][key_alfa]
        for i in range(len(e_acc))
    ]
    ax.plot(e_acc, alfas, label=label)
    ax.grid(True)
    ax.set_xlabel(r"$E_{acc}$ [MV/m]")
    ax.set_ylabel(r"$\alpha$ [1/ns]")
    ax.legend()

    if savedat:
        save_me = np.column_stack((e_acc, alfas))
        np.savetxt(Path(basefolder, "..", "exp_growth.txt"), save_me)
