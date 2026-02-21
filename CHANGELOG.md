# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.7.8] - 2026-02-21

### Changed

- **Sensors**: Updated `timestamp` attribute to include the year. New format: **DD/MM/YYYY HH:MM** (e.g., "24/02/2026 20:30").

## [1.7.7] - 2026-02-21

### Changed

- **Sensors**: Enhanced `timestamp` attribute to include both date and time (e.g., "24/02 20:30") for a more complete view and easier dashboard integration.

## [1.7.6] - 2026-02-21

### Changed

- **Sensors**: Simplified match timestamps. The `timestamp` attribute now contains the localized time (e.g., "20:30") directly, making it easier to use in Home Assistant cards.
  - Match Sensor: `timestamp` now holds localized time.
  - League Table: `next_time` renamed to `timestamp` for consistency across rows.

## [1.7.5] - 2026-02-21

### Fixed

- **Core**: Fixed `NameError: name 'logging' is not defined` in `sensor.py`. Emergency fix for integration startup failure.

## [1.7.4] - 2026-02-21

### Added

- **Time Localization**: All UTC timestamps (matches, fixtures) are now automatically converted to the user's local timezone (e.g., Romania Time).
  - New `local_time` attribute in Match sensor.
  - New `next_time` attribute in League Table rows.

## [1.7.3] - 2026-02-21

### Fixed

- **League Table**: Fixed missing opponent logos in the "Next" column.
  - Root cause: Incorrect data index used for opponent team ID extraction.

## [1.7.1] - 2026-02-21

### Fixed

**Form Sensor**:

- Fixed `sensor.team_form` returning `N/A` for all teams.
- Root cause: `teamForm` data lives at `table_container` level (sibling of `data`), not inside `data.table`.
- Both `FotMobTeamFormSensor` and `FotMobLeagueTableSensor` now read from the correct data path.
- League table "Form" column is now populated correctly for all teams.

## [1.7.0] - 2026-02-21

### Added

- **League Table Fetch**: Coordinator now fetches full league table data from FotMob `/api/leagues` endpoint.
- **High-Fidelity Form Data**: Form sensor now merges data from the league API's `teamForm` dictionary.

### Fixed

- **Form Sensor**: Improved fallback logic for extracting form results from multiple data sources.

## [1.6.9] - 2026-02-21

### Added

- **Ultra High-Fidelity League Table**: Implemented multi-list merging strategy to populate "Form" and "Next Match" columns.
- Data merge for separate `form` and `nextOpponent` objects in FotMob API responses.

## [1.6.8] - 2026-02-21

### Added

- **League Table Sensor**: New sensor providing full league standings as a structured attribute.
- **Markdown Table Template**: Example Markdown card template for displaying the league table in dashboards.

### Changed

- Default update interval reduced to 1 minute for near real-time score updates.

## [1.6.7] - 2026-02-20

### Fixed

- Improved error handling when FotMob API returns partial or malformed data.

## [1.6.6] - 2026-02-20

### Fixed

- Fixed sensor crash when team data fields are missing from the API response.

## [1.6.5] - 2026-02-20

### Fixed

- Sensor crash when team data was partially missing or incomplete.

## [1.6.4] - 2026-02-20

### Changed

- Improved Top Scorer and Top Rating sensor reliability with better fallback logic.

## [1.6.3] - 2026-02-20

### Added

- **Top Rating Sensor**: Shows the highest-rated player and their rating.

## [1.6.2] - 2026-02-20

### Added

- **Top Scorer Sensor**: Shows the team's top scorer and their goal count.

## [1.6.1] - 2026-02-20

### Added

- **Matches Played Sensor**: Tracks total matches played in the current season.
- **Team Form Sensor**: Shows recent match results (W/D/L).

## [1.6.0] - 2026-02-20

### Added

- **DataUpdateCoordinator**: Centralized data fetching for efficient API polling.
- **League Position Sensor**: Shows current league standing position.
- **League Points Sensor**: Shows total league points.
- **Transfers Sensor**: Shows recent player transfers (in/out).
- **History Sensor**: Shows historical season results.

## [1.5.1] - 2026-02-20

### Fixed

- HACS compliance fixes for `manifest.json` and `hacs.json`.

## [1.5.0] - 2026-02-20

### Added

- **Config Flow UI**: Full UI-based setup — no YAML configuration needed.
- Team search by name during setup.

### Changed

- Upgraded from YAML-only to config entry-based integration.

## [1.4.0] - 2026-02-20

### Added

- **HACS Support**: Added `hacs.json` for HACS repository compatibility.
- Professional README with installation instructions.

## [1.3.0] - 2026-02-20

### Changed

- **Enhanced Match Sensor**: Match description shown as state with live score support.
- Improved sensor attributes with detailed match information.

## [1.2.0] - 2026-02-20

### Added

- Initial HACS-compliant release.
- Basic next match sensor for FotMob teams.
- `manifest.json` with proper domain and requirements.
