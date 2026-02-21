# FotMob Fixtures Home Assistant Integration

This custom component for Home Assistant allows you to track upcoming matches for any football team using data from [FotMob](https://www.fotmob.com/).

<img width="256" height="256" alt="logo" src="https://github.com/user-attachments/assets/939ac7f9-4249-41f4-b4cb-f952a2a55838" />


## Features

- **UI-Based Configuration**: No YAML required! Setup teams directly via the Home Assistant Integrations page.
- **12 specialized Sensors**: Track Match details, League Position, Points, Form, Matches Played, Top Scorer, Top Rating, Transfers, History, Complete League Table, Stadium, and Coach.
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

The integration creates 12 sensors for each team:

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
| `League Table` | Full league standings and stats | `3` (Position) |
| `Stadium` | Team's home stadium details | `Stadium Name` |
| `Coach` | Team's current head coach | `Coach Name` |

### Match Sensor Attributes

The primary Match sensor provides rich metadata:

- `team_name`: Name of the tracked team.
- `opponent`: Name of the opponent.
- `opponent_logo`: URL to the opponent's logo.
- `home_away`: "Home" or "Away".
- `league`: Competition name (Premier League, La Liga, etc.).
- `match`: Full match name.
- `timestamp`: Match start time in local timezone (`DD/MM/YYYY HH:MM GMT+2`).
- `status`: `Live` or `Scheduled`.
- `score`: Current score string.
- `opponent_rank`: Opponent's league rank.
- `opponent_form`: Opponent's recent form.
- `difficulty`: Match difficulty (`High`, `Medium`, `Low`).

  DASHBOARD Exemple:
```
  views:
  - sections:
      - cards:
          - type: heading
            heading: ⚽ Următorul Meci
          - type: markdown
            content: >-
              ## 🆚 {{ state_attr('sensor.rapid_bucuresti_match', 'match') }}
              **🏟️ {{ state_attr('sensor.rapid_bucuresti_match', 'home_away')
              }}**
              {% if state_attr('sensor.rapid_bucuresti_match', 'timestamp') %}
              **⏰ Ora:** {{ state_attr('sensor.rapid_bucuresti_match',
              'timestamp') }}
              {% endif %}
              **📊 Status:** {{ state_attr('sensor.rapid_bucuresti_match',
              'status') }}
              {% if state_attr('sensor.rapid_bucuresti_match', 'score') %}
              **⚽ Scor:** {{ state_attr('sensor.rapid_bucuresti_match', 'score')
              }}
              {% endif %}
              ---
              **vs {{ state_attr('sensor.rapid_bucuresti_match', 'opponent')
              }}**
              - Loc în clasament: {{ state_attr('sensor.rapid_bucuresti_match',
              'opponent_rank') }}
              - Formă: {% for r in state_attr('sensor.rapid_bucuresti_match',
              'opponent_form') %}{%- set c = '#4CAF50' if r == 'W' else
              ('#FF9800' if r == 'D' else '#F44336') -%}<span
              style="background:{{c}};color:white;padding:2px
              5px;border-radius:3px;font-size:0.8em;">{{r}}</span> {% endfor %}
              - Dificultate: {{ state_attr('sensor.rapid_bucuresti_match',
              'difficulty') }}
          - type: markdown
            content: >-
              ## 🏟️ Stadion
              **{{ states('sensor.rapid_bucuresti_stadium') }}**
              📍 {{ state_attr('sensor.rapid_bucuresti_stadium', 'city') }}, {{
              state_attr('sensor.rapid_bucuresti_stadium', 'country') }}
              👥 Capacitate: {{ state_attr('sensor.rapid_bucuresti_stadium',
              'capacity') }} locuri
      - cards:
          - type: heading
            heading: 📈 Statistici Rapid
          - type: grid
            cards:
              - type: custom:mushroom-entity-card
                entity: sensor.rapid_bucuresti_points
                icon: mdi:numeric
                icon_color: yellow
                name: Puncte
                fill_container: true
              - type: custom:mushroom-entity-card
                entity: sensor.rapid_bucuresti_position
                icon: mdi:format-list-numbered
                icon_color: blue
                name: Loc
                fill_container: true
              - type: custom:mushroom-entity-card
                entity: sensor.rapid_bucuresti_played
                icon: mdi:soccer-field
                icon_color: orange
                name: Meciuri
                fill_container: true
            title: Performanță
          - type: custom:mushroom-entity-card
            entity: sensor.rapid_bucuresti_top_scorer
            icon: mdi:soccer
            icon_color: red
            name: Golgheter
            fill_container: true
            layout: vertical
          - type: custom:mushroom-entity-card
            entity: sensor.rapid_bucuresti_top_rating
            icon: mdi:star
            icon_color: yellow
            name: Best Player
            fill_container: true
            layout: vertical
          - type: custom:mushroom-entity-card
            entity: sensor.rapid_bucuresti_coach
            icon: mdi:account-tie
            icon_color: purple
            name: Antrenor
            fill_container: true
            layout: vertical
          - type: custom:mushroom-entity-card
            entity: sensor.rapid_bucuresti_top_assist
            icon: mdi:handshake
            icon_color: cyan
            name: Top Assist
            fill_container: true
            layout: vertical
      - cards:
          - type: heading
            heading: 🔄 Transferuri & Istoric
          - type: markdown
            content: >
              ## 🔄 Transferuri Rapids
              **📥 Sosiri:** {% for player in
              state_attr('sensor.rapid_bucuresti_transfers', 'players_in')[:3]
              %} • {{ player.name }} ({{ player.position.label }}) - de la {{
              player.fromClub }} {% endfor %}
              **📤 Plecări:** {% for player in
              state_attr('sensor.rapid_bucuresti_transfers', 'players_out')[:3]
              %} • {{ player.name }} ({{ player.position.label }}) - la {{
              player.toClub }} {% endfor %}
          - type: markdown
            content: >-
              ## 🏆 Trofee Rapid București (14)
              {% for trophy in state_attr('sensor.rapid_bucuresti_history',
              'trophies') %}
              **{{ trophy.name }}: {{ trophy.count }}** 
              {{ trophy.seasons }}
              {% endfor %}
          - type: markdown
            content: >-
              ## 📊 Ultimele 5 Meciuri
              {% for match in state_attr('sensor.rapid_bucuresti_form',
              'form_list') %}
              {% if match.home.isOurTeam %}{{ match.away.name }} (D) - {{
              match.score }}{% else %}{{ match.home.name }} (A) - {{ match.score
              }}{% endif %} - {{ '🟢' if match.resultString == 'W' else ('🟡' if
              match.resultString == 'D' else '🔴') }} {{ match.resultString }}
              {% endfor %}
      - cards:
          - type: markdown
            content: >
              # <img src="{{ state_attr('sensor.rapid_bucuresti_league_table',
              'entity_picture') }}" width="30"> Clasament {{
              state_attr('sensor.rapid_bucuresti_league_table', 'league_name')
              }}
              |   | # | Echipa | M | G | P | Formă |
              |:---:|:---:|:---|:---:|:---:|:---:|:---:|
              {% for entry in state_attr('sensor.rapid_bucuresti_league_table',
              'table') | default([]) -%}
              {%- set rank_num = entry.rank | int -%}
              {%- set icon = '🟦' if rank_num <= 6 else '🟨' -%}
              | {{ icon }} | {{ entry.rank }} | <img
              src="https://images.fotmob.com/image_resources/logo/teamlogo/{{
              entry.team_id }}.png" width="20"> {{ '**' if entry.is_current }}{{
              entry.team }}{{ '**' if entry.is_current }} | {{ entry.played }} |
              {{ entry.gd }} | **{{ entry.pts }}** | {% if entry.form is defined
              %}{% for res in entry.form %}{%- set c = '#4CAF50' if res == 'W'
              else ('#FF9800' if res == 'D' else '#F44336') -%}<span
              style="background-color:{{c}};color:white;padding:1px
              3px;border-radius:3px;font-size:0.8em;font-weight:bold;">{{'V' if
              res == 'W' else ('E' if res == 'D' else 'I')}}</span> {% endfor
              %}{% endif %} |
              {% endfor %}
              **Legendă:** 🟦 Play-Off (1-6) &nbsp; 🟨 Play-Out (7-16)
    type: sections
    max_columns: 2
    cards: []
```

## Credits

Data provided by [FotMob](https://www.fotmob.com/).
