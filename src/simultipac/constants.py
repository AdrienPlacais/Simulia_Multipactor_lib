"""Define some constants."""

clight = 299_792_458.0
clight_in_mm_per_ns = clight * 1e-6
qelem = 1.6021766e-19

markdown: dict[str, str] = {
    "alpha": r"$\alpha$ [ns$^{-1}$]",
    "e_acc": "$E_{acc}$ [V/m]",
    "population": "$n_e$",
    "time": "$t$ [ns]",
}
