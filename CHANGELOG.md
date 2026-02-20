# Changelog

All notable changes to this project will be documented in this file.

## [1.6.9] - 2026-02-21

### Added

- **Ultra High-Fidelity League Table**: Implemented a multi-list merging strategy to populate "Form" and "Next Match" columns for leagues like Romania Liga I.
- Data merge for separate `form` and `nextOpponent` objects in FotMob API.

## [1.6.8] - 2026-02-21

### Added

- **League Table Support**: Added a new sensor that provides full league standings.
- **Improved Update Frequency**: Set default update interval to 1 minute for near real-time scores.

## [1.6.5] - 2026-02-20

### Fixed

- Sensor crash when team data was partially missing.

## [1.6.0] - 2026-02-20

### Added

- Initial support for FotMob fixtures and team data.
- Basic sensor implementation.
