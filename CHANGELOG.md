# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

# [2.0.x]

## [2.0.2] -- 2025-04-14

### Added

- The package is available on PyPI and can be downloaded with: `pip install simultipac`.

Modernize and package the library.

## [2.0.1] -- 2025-04-14

### Added

- `SimulationResults` and `ParticleMonitor` can be initialized with the `load_first_n_particles`.
  Will only load the first `load_first_n_particles` in `folder_particle_monitor` to speed up the script for debug purposes.

### Changed

- UI is more natural. In particular:
    - Simulation results are stored in appropriate `SimulationResults`; a bunch of `SimulationResults` are stored to `SimulationsResults` objects.
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
