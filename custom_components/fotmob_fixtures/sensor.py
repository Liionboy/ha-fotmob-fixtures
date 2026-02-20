import logging
from datetime import datetime

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_TEAM_ID

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    team_id = config_entry.data.get(CONF_TEAM_ID)
    
    entities = [
        FotMobMatchSensor(coordinator, team_id),
        FotMobLeaguePositionSensor(coordinator, team_id),
        FotMobLeaguePointsSensor(coordinator, team_id),
        FotMobTeamFormSensor(coordinator, team_id),
        FotMobMatchesPlayedSensor(coordinator, team_id),
        FotMobTopScorerSensor(coordinator, team_id),
        FotMobTopRatingSensor(coordinator, team_id),
        FotMobTeamTransfersSensor(coordinator, team_id),
        FotMobTeamHistorySensor(coordinator, team_id),
        FotMobLeagueTableSensor(coordinator, team_id),
    ]
    
    async_add_entities(entities)

class FotMobBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for FotMob sensors."""

    def __init__(self, coordinator, team_id):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._team_id = team_id
        self._attr_unique_id = f"fotmob_{team_id}_{self.entity_description_key}"

    @property
    def team_data(self):
        """Return the data for this team."""
        return self.coordinator.data if self.coordinator.data is not None else {}

    @property
    def team_name(self):
        """Return the name of the team."""
        return self.team_data.get('details', {}).get('name', 'FotMob Team')

    @property
    def entity_picture(self):
        """Return the logo of the tracked team."""
        return f"https://images.fotmob.com/image_resources/logo/teamlogo/{self._team_id}.png"

class FotMobMatchSensor(FotMobBaseSensor):
    """Sensor for the next or live match."""

    entity_description_key = "match"

    @property
    def name(self):
        return f"{self.team_name} Match"

    @property
    def state(self):
        data = self.team_data
        fixtures = data.get('fixtures', {}).get('allFixtures', {}).get('fixtures', [])
        
        active_match = None
        upcoming_matches = []
        
        for fix in fixtures:
            status = fix.get('status', {})
            if status.get('started') and not status.get('finished'):
                active_match = fix
                break
            if not status.get('started'):
                upcoming_matches.append(fix)
        
        match_to_track = active_match or (upcoming_matches[0] if upcoming_matches else None)
        
        if match_to_track:
            status = match_to_track.get('status', {})
            home_team = match_to_track.get('home', {}).get('name')
            away_team = match_to_track.get('away', {}).get('name')
            
            if status.get('started') and not status.get('finished'):
                score = status.get('scoreStr', '0 - 0')
                return f"LIVE: {score}"
            return f"{home_team} vs {away_team}"
        
        return "No upcoming matches"

    @property
    def extra_state_attributes(self):
        data = self.team_data
        fixtures = data.get('fixtures', {}).get('allFixtures', {}).get('fixtures', [])
        
        active_match = None
        upcoming_matches = []
        
        for fix in fixtures:
            status = fix.get('status', {})
            if status.get('started') and not status.get('finished'):
                active_match = fix
                break
            if not status.get('started'):
                upcoming_matches.append(fix)
        
        match = active_match or (upcoming_matches[0] if upcoming_matches else None)
        if not match:
            return {}

        status = match.get('status', {})
        home_id = match.get('home', {}).get('id')
        is_home = str(home_id) == str(self._team_id)
        opponent = match.get('away', {}).get('name') if is_home else match.get('home', {}).get('name')
        opponent_id = match.get('away', {}).get('id') if is_home else match.get('home', {}).get('id')

        return {
            "opponent": opponent,
            "opponent_logo": f"https://images.fotmob.com/image_resources/logo/teamlogo/{opponent_id}.png",
            "home_away": "Home" if is_home else "Away",
            "league": match.get('league', {}).get('name'),
            "match": f"{match.get('home', {}).get('name')} vs {match.get('away', {}).get('name')}",
            "timestamp": status.get('utcTime'),
            "status": "Live" if (status.get('started') and not status.get('finished')) else "Scheduled",
            "score": status.get('scoreStr')
        }

class FotMobLeaguePositionSensor(FotMobBaseSensor):
    """Sensor for league position."""
    entity_description_key = "position"

    @property
    def name(self):
        return f"{self.team_name} Position"

    @property
    def state(self):
        table = self.team_data.get('overview', {}).get('table', [{}])[0].get('data', {}).get('table', {}).get('all', [])
        for entry in table:
            if str(entry.get('id')) == str(self._team_id):
                return entry.get('idx')
        return None

    @property
    def icon(self):
        return "mdi:format-list-numbered"

class FotMobLeaguePointsSensor(FotMobBaseSensor):
    """Sensor for league points."""
    entity_description_key = "points"

    @property
    def name(self):
        return f"{self.team_name} Points"

    @property
    def state(self):
        table = self.team_data.get('overview', {}).get('table', [{}])[0].get('data', {}).get('table', {}).get('all', [])
        for entry in table:
            if str(entry.get('id')) == str(self._team_id):
                return entry.get('pts')
        return None

    @property
    def icon(self):
        return "mdi:numeric"

class FotMobTeamFormSensor(FotMobBaseSensor):
    """Sensor for team form."""
    entity_description_key = "form"

    @property
    def name(self):
        return f"{self.team_name} Form"

    @property
    def state(self):
        # Search all tables in overview
        tables = self.team_data.get('overview', {}).get('table', [])
        for table_container in tables:
            rows = table_container.get('data', {}).get('table', {}).get('all', [])
            for entry in rows:
                if str(entry.get('id')) == str(self._team_id):
                    form = entry.get('deductionReason') or entry.get('form', [])
                    if isinstance(form, list):
                        return "-".join([f.get('result', '?') for f in form])
                    return form
        return "N/A"

    @property
    def extra_state_attributes(self):
        # Add detailed form attributes for debugging and better UI
        tables = self.team_data.get('overview', {}).get('table', [])
        for table_container in tables:
            rows = table_container.get('data', {}).get('table', {}).get('all', [])
            for entry in rows:
                if str(entry.get('id')) == str(self._team_id):
                    return {
                        "form_list": entry.get('form', []),
                        "deduction": entry.get('deductionReason')
                    }
        return {}

    @property
    def icon(self):
        return "mdi:chart-line"

class FotMobMatchesPlayedSensor(FotMobBaseSensor):
    """Sensor for matches played."""
    entity_description_key = "played"

    @property
    def name(self):
        return f"{self.team_name} Played"

    @property
    def state(self):
        tables = self.team_data.get('overview', {}).get('table', [])
        for table_container in tables:
            rows = table_container.get('data', {}).get('table', {}).get('all', [])
            for entry in rows:
                if str(entry.get('id')) == str(self._team_id):
                    return entry.get('played')
        return None

    @property
    def icon(self):
        return "mdi:soccer-field"

class FotMobTopScorerSensor(FotMobBaseSensor):
    """Sensor for top scorer."""
    entity_description_key = "top_scorer"

    @property
    def name(self):
        return f"{self.team_name} Top Scorer"

    @property
    def state(self):
        players = self.team_data.get('overview', {}).get('topPlayers', {}).get('byGoals', {}).get('players', [])
        if players:
            player = players[0]
            name = player.get('name', 'N/A')
            goals = player.get('rank', 0) # API uses 'rank' as goal count in some contexts
            return f"{name} ({goals} goals)"
        return "N/A"

    @property
    def icon(self):
        return "mdi:star-circle"

class FotMobTopRatingSensor(FotMobBaseSensor):
    """Sensor for top rating."""
    entity_description_key = "top_rating"

    @property
    def name(self):
        return f"{self.team_name} Top Rating"

    @property
    def state(self):
        players = self.team_data.get('overview', {}).get('topPlayers', {}).get('byRating', {}).get('players', [])
        if players:
            player = players[0]
            name = player.get('name', 'N/A')
            rating = player.get('rank', '0.0')
            return f"{name} ({rating})"
        return "N/A"

    @property
    def icon(self):
        return "mdi:trending-up"

class FotMobTeamTransfersSensor(FotMobBaseSensor):
    """Sensor for team transfers."""
    entity_description_key = "transfers"

    @property
    def name(self):
        return f"{self.team_name} Transfers"

    @property
    def state(self):
        transfers = self.team_data.get('transfers', {}).get('data', {})
        players_in = transfers.get('Players in', [])
        if players_in:
            return players_in[0].get('name', 'N/A')
        return "No recent transfers"

    @property
    def extra_state_attributes(self):
        transfers = self.team_data.get('transfers', {}).get('data', {})
        return {
            "players_in": transfers.get('Players in', []),
            "players_out": transfers.get('Players out', []),
            "contract_extensions": transfers.get('Contract extensions', [])
        }

    @property
    def icon(self):
        return "mdi:transfer"

class FotMobTeamHistorySensor(FotMobBaseSensor):
    """Sensor for team history (trophies)."""
    entity_description_key = "history"

    @property
    def name(self):
        return f"{self.team_name} History"

    @property
    def state(self):
        history = self.team_data.get('history', {})
        trophies = history.get('trophyList', [])
        total = 0
        for t in trophies:
            won = t.get('won', [])
            if isinstance(won, list) and len(won) > 0:
                try:
                    total += int(won[0])
                except (ValueError, TypeError):
                    pass
        return total

    @property
    def extra_state_attributes(self):
        history = self.team_data.get('history', {})
        trophies = history.get('trophyList', [])
        
        flattened_trophies = []
        for t in trophies:
            name_list = t.get("name", ["N/A"])
            won_list = t.get("won", ["0"])
            season_list = t.get("season_won", [""])
            
            name = name_list[0] if isinstance(name_list, list) and name_list else "N/A"
            count_str = won_list[0] if isinstance(won_list, list) and won_list else "0"
            seasons = season_list[0] if isinstance(season_list, list) and season_list else ""
            
            try:
                count = int(count_str)
            except (ValueError, TypeError):
                count = 0
                
            flattened_trophies.append({
                "name": name,
                "count": count,
                "seasons": seasons
            })
            
        return {
            "trophies": flattened_trophies
        }

    @property
    def icon(self):
        return "mdi:trophy"

class FotMobLeagueTableSensor(FotMobBaseSensor):
    """Sensor for full league table."""
    entity_description_key = "league_table"

    @property
    def name(self):
        return f"{self.team_name} League Table"

    @property
    def state(self):
        # Search all tables in overview
        tables = self.team_data.get('overview', {}).get('table', [])
        for table_container in tables:
            rows = table_container.get('data', {}).get('table', {}).get('all', [])
            for entry in rows:
                if str(entry.get('id')) == str(self._team_id):
                    return entry.get('idx')
        return None

    @property
    def extra_state_attributes(self):
        # 1. Try to get data from the full league_table fetch first
        league_data = self.team_data.get('league_table', {})
        tables = league_data.get('table', [])
        
        # If league_table fetch failed or is missing, fallback to overview table
        if not tables:
            tables = self.team_data.get('overview', {}).get('table', [])
            
        if not tables:
            return {"league_name": "N/A", "table": []}
            
        # We prefer the table that contains our team
        league_info = {}
        rows = []
        table_data_obj = {}
        for table_container in tables:
            t_data = table_container.get('data', {}).get('table', {})
            current_rows = t_data.get('all', [])
            if any(str(row.get('id')) == str(self._team_id) for row in current_rows):
                league_info = table_container.get('data', {})
                table_data_obj = t_data
                rows = current_rows
                break
        
        if not rows and tables:
            league_info = tables[0].get('data', {})
            table_data_obj = league_info.get('table', {})
            rows = table_data_obj.get('all', [])
        
        # High-Fidelity Merge: Create maps for form and next opponents
        form_map = {}
        # 'form' is often a list of dicts with team IDs
        for f_entry in table_data_obj.get('form', []):
            t_id = str(f_entry.get('id'))
            form_map[t_id] = f_entry.get('form', [])
            
        next_map = {}
        # 'nextOpponent' is often a dict keyed by team ID
        # Format: { team_id: [fixture_id, time, opponent_id, opponent_name, ...] }
        next_obj = table_data_obj.get('nextOpponent')
        if isinstance(next_obj, dict):
            for t_id, data in next_obj.items():
                if isinstance(data, list) and len(data) >= 3:
                    next_map[str(t_id)] = data[2] # Opponent Team ID
        
        formatted_table = []
        for row in rows:
            t_id = str(row.get('id'))
            
            # 1. Extract form (prefer merge, fallback to row-local)
            form_results = []
            raw_form = form_map.get(t_id) or row.get('form', [])
            
            if isinstance(raw_form, list):
                for f in raw_form:
                    if isinstance(f, dict):
                        form_results.append(f.get('resultString', f.get('result', '?')))
                    elif isinstance(f, str):
                        form_results.append(f)
                    else:
                        form_results.append('?')

            # 2. Extract next opponent (prefer merge, fallback to row-local)
            next_id = next_map.get(t_id)
            if not next_id:
                next_opponent = row.get("next")
                if isinstance(next_opponent, list) and len(next_opponent) > 0:
                    next_id = next_opponent[0].get("id")
                elif isinstance(next_opponent, (str, int)):
                    next_id = next_opponent

            formatted_table.append({
                "rank": row.get("idx"),
                "team": row.get("name"),
                "team_id": row.get("id"),
                "played": row.get("played"),
                "wins": row.get("wins"),
                "draws": row.get("draws"),
                "losses": row.get("losses"),
                "goals": row.get("scoresStr", "-"),
                "gd": row.get("goalConDiff"),
                "pts": row.get("pts"),
                "form": form_results,
                "next_id": next_id,
                "color": row.get("qualColor") or row.get("color") or "", 
                "deduction": row.get("deductionReason"),
                "is_current": t_id == str(self._team_id)
            })
            
        return {
            "league_name": league_info.get("leagueName", "N/A"),
            "table": formatted_table
        }

    @property
    def icon(self):
        return "mdi:table-large"
