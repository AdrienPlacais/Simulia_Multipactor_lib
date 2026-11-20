<!-- markdownlint-disable MD024 -->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

# [2.1.x]

- Implement new functionalities:
  - Surface distribution of TEEY.

## [2.1.2] -- 2026-11-20

### Added

- Use the keyword `aggregate=True` on `SimulationsResults.plot` with 0D data,
  when several simulations with the same parameters were performed, to show
  medians and standard deviations.
  - Typical use case: several simulations were performed for better
    representativeness, and you want to plot exponential
    growth factor vs power or accelerating field.

### Fixed

- When loading `SimulationsResults` from a CST folder, a directory with missing
  data is now skipped instead of raising an error. A warning is logged if the name
  of the directory does not start with a period.
  - Typical use case: you want to keep data in a `.archive` folder.

## [2.1.1] -- 2026-11-17

### Added

- More explicit warning when fitting range exceeds simulation time.
- Possibility to choose unit of accelerating field. `Parameters.txt` do not
  always hold expected units.
- Instantiate `SimulationResult` with power instead of accelerating field.

## [2.1.0] -- 2025-10-24

### Added

- Better documentation on SPARK3D files.

### Fixed

- Set up different default values in the fitting process for SPARK3D and CST.
  Avoids unnecessary warnings with SPARK3D.
- Different delimiters in SPARK3D `TXT` and `CSV` files is handled.

## [2.0.3] -- 2025-04-14

### Changed

- Simpler release workflow.

## [2.0.2] -- 2025-04-14

### Added

- The package is available on PyPI and can be downloaded with: `pip install
simultipac`.

## [2.0.1] -- 2025-04-14

### Added

- `SimulationResults` and `ParticleMonitor` can be initialized with the
  `load_first_n_particles`. Will only load the first `load_first_n_particles` in
  `folder_particle_monitor` to speed up the script for debug purposes.

### Changed

- UI is more natural. In particular:
  - Simulation results are stored in appropriate `SimulationResults`; a bunch of
    `SimulationResults` are stored to `SimulationsResults` objects.
- Factories allow easy creation of these objects.
  - They have `plot`, `hist` and `fit_alpha` methods.
  - Same functionalities can be achieved with way less lines of code.
- Use `logging` module instead of color printed messages.

## [2.0.0] -- 2025-01-31

### Changed

- Library is properly packaged. New module name is `simultipac`.
- Documentation is hosted on read the docs and automatically updated.

<!-- ## [0.0.0] 1312-01-01 -->
<!---->
<!-- ### Added -->
<!---->
<!-- ### Changed -->
<!---->
<!-- ### Deprecated -->
<!---->
<!-- ### Removed -->
<!---->
<!-- ### Fixed -->
<!---->
<!-- ### Security -->
