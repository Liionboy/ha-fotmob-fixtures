# FotMob Fixtures Home Assistant Integration

This custom component for Home Assistant allows you to track upcoming matches for any football team using data from [FotMob](https://www.fotmob.com/).

![FotMob Dashboard Example](https://images.fotmob.com/image_resources/logo/teamlogo/9738.png)

## Features

- **UI-Based Configuration**: No YAML required! Setup teams directly via the Home Assistant Integrations page.
- **Track Any Team**: Simply provide a FotMob Team ID.
- **Rich Attributes**: Provides match time, opponent name, opponent logo, competition name, and home/away status.
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
5. (Optional) Provide a custom name for the sensor.
6. Click **Submit**.

## How to Find Your Team ID

1. Go to [fotmob.com](https://www.fotmob.com).
2. Use the search bar to find your favorite team (e.g., "Real Madrid").
3. Look at the browser URL. It will look like this:
   `https://www.fotmob.com/teams/8633/overview/real-madrid`
4. The number between `/teams/` and `/overview/` is your **Team ID** (in this example, `8633`).

## Sensor Entities

The integration creates a sensor: `sensor.[team_name]_next_match`.

### Attributes

- `team_name`: Name of the tracked team.
- `opponent`: Name of the opponent.
- `opponent_logo`: URL to the opponent's logo.
- `home_away`: "Home" or "Away".
- `league`: Competition name (Premier League, La Liga, etc.).
- `match`: Full match name.
- `timestamp`: Match start time in ISO format.

## Credits

Data provided by [FotMob](https://www.fotmob.com/).
