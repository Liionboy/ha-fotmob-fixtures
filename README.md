# FotMob Fixtures Home Assistant Integration

This custom component for Home Assistant allows you to track upcoming matches for any football team using data from [FotMob](https://www.fotmob.com/).

![FotMob Fixtures Banner](https://images.unsplash.com/photo-1574629810360-7efbbe195018?q=80&w=2693&auto=format&fit=crop)

## Features

- **UI-Based Configuration**: No YAML required! Setup teams directly via the Home Assistant Integrations page.
- **7 specialized Sensors**: Track Match details, League Position, Points, Form, Matches Played, Top Scorer, and Top Rating.
- **LIVE Match Support**: Real-time scores and status updates during the match.
- **Efficient Data Fetching**: Uses a centralized `DataUpdateCoordinator` to fetch all team data in a single API call per minute.
- **Rich Attributes**: Comprehensive match details, opponent logos, and competition info.
- **HACS Support**: Easy installation and updates through HACS.

## Installation

### Method 1: HACS (Recommended)

1. Ensure [HACS](https://hacs.xyz/) is installed and working.
2. Go to **HACS** -> **Integrations**.
3. Click the three dots (top right) -> **Custom repositories**.
4. Paste this URL: `https://github.com/Liionboy/ha-fotmob-fixtures`
5. Select **Integration** as the category and click **Add**.
6. Find **FotMob Fixtures** in the HACS list and click **Download**.
7. Restart Home Assistant.

### Method 2: Manual

1. Download the `fotmob_fixtures` folder from this repository.
2. Copy it into your Home Assistant's `config/custom_components/` directory.
3. Restart Home Assistant.

## Configuration

1. In the Home Assistant UI, navigate to **Settings** -> **Devices & Services**.
2. Click **Add Integration** in the bottom right.
3. Search for **FotMob Fixtures**.
4. Enter the **Team ID** for the team you want to track.
5. Click **Submit**.

## How to Find Your Team ID

1. Go to [fotmob.com](https://www.fotmob.com).
2. Use the search bar to find your favorite team (e.g., "Real Madrid").
3. Look at the browser URL. It will look like this:
   `https://www.fotmob.com/teams/8633/overview/real-madrid`
4. The number between `/teams/` and `/overview/` is your **Team ID** (in this example, `8633`).

## Sensor Entities

The integration creates 7 sensors for each team:

| Sensor | Description | Example State |
| --- | --- | --- |
| `Match` | Current LIVE score or next scheduled match | `LIVE: 2 - 1` or `Team A vs Team B` |
| `Position` | Current league position | `3` |
| `Points` | Current league points | `55` |
| `Form` | Recent results (Win/Draw/Loss) | `W-D-W-L-W` |
| `Played` | Total matches played in the league | `25` |
| `Top Scorer` | Team's top scorer and goal count | `Player Name (12 goals)` |
| `Top Rating` | Highest rated player in the team | `Player Name (8.5)` |
| `Transfers` | Most recent incoming transfer | `Player Name` |
| `History` | Total number of trophies won | `12` |

### Match Sensor Attributes

The primary Match sensor provides rich metadata:

- `team_name`: Name of the tracked team.
- `opponent`: Name of the opponent.
- `opponent_logo`: URL to the opponent's logo.
- `home_away`: "Home" or "Away".
- `league`: Competition name (Premier League, La Liga, etc.).
- `match`: Full match name.
- `timestamp`: Match start time in ISO format.
- `status`: `Live` or `Scheduled`.
- `score`: Current score string.

## Credits

Data provided by [FotMob](https://www.fotmob.com/).
