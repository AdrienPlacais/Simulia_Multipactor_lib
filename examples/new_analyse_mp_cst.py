"""Define the interface of the new code."""

from pathlib import Path

from simultipac.simulation_results.simulations_results import (
    SimulationsResults,
    SimulationsResultsFactory,
)

if __name__ == "__main__":
    factory = SimulationsResultsFactory("CST", freq_ghz=1.30145)
    results: SimulationsResults = factory.create(
        master_folder=Path("cst/Export_Parametric"),
    )
    idx_to_plot = (0, 5, 90)
    axes = results.plot(
        x="time", y="population", idx_to_plot=idx_to_plot, alpha=0.7
    )

    results.fit_alpha(fitting_periods=5, minimum_final_number_of_electrons=5)
    results.plot(
        x="time",
        y="modelled_population",
        idx_to_plot=idx_to_plot,
        axes=axes,
        lw=3,
        ls="--",
    )
    # results.plot(x="e_acc", y="alpha")
    # results.save(
    #     "growth.txt",
    #     *(
    #         "e_acc",
    #         "alpha",
    #     ),
    #     delimiter="\t",
    # )
