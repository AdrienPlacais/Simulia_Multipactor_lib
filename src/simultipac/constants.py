"""Define some constants."""

clight = 299_792_458.0
clight_in_mm_per_ns = clight * 1e-6
qelem = 1.6021766e-19

#: Associates name of variables in the library to markdown formatted strings
markdown: dict[str, str] = {
    "alpha": r"$\alpha$ [ns$^{-1}$]",
    "collision_angle": r"Impact angle $\theta$ [deg]",
    "collision_energy": "Collision energy [eV]",
    "e_acc": "$E_{acc}$ [V/m]",
    "emission_energy": "Emission energy [eV]",
    "population": "$n_e$",
    "time": "$t$ [ns]",
}
