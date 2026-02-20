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
        return self.coordinator.data

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
        table = self.team_data.get('overview', {}).get('table', [{}])[0].get('data', {}).get('table', {}).get('all', [])
        for entry in table:
            if str(entry.get('id')) == str(self._team_id):
                form = entry.get('deductionReason') or entry.get('form', []) # FotMob often uses deductionReason if something is weird, but usually form is a list
                if isinstance(form, list):
                    return "-".join([f.get('result', '?') for f in form])
                return form
        return None

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
        table = self.team_data.get('overview', {}).get('table', [{}])[0].get('data', {}).get('table', {}).get('all', [])
        for entry in table:
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
            return f"{player.get('name')} ({player.get('rank')} goals)"
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
            return f"{player.get('name')} ({player.get('rank')})"
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
        total_trophies = sum([int(t.get('won', ['0'])[0]) for t in trophies])
        return total_trophies

    @property
    def extra_state_attributes(self):
        history = self.team_data.get('history', {})
        trophies = history.get('trophyList', [])
        
        # Flatten the list-based structure from FotMob
        flattened_trophies = []
        for t in trophies:
            flattened_trophies.append({
                "name": t.get("name", ["N/A"])[0],
                "count": int(t.get("won", ["0"])[0]),
                "seasons": t.get("season_won", [""])[0]
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
        # State is the current team's position
        overview = self.team_data.get('overview', {})
        table_data = overview.get('table', [{}])
        if not table_data:
            return None
            
        rows = table_data[0].get('data', {}).get('table', {}).get('all', [])
        for entry in rows:
            if str(entry.get('id')) == str(self._team_id):
                return entry.get('idx')
        return None

    @property
    def extra_state_attributes(self):
        overview = self.team_data.get('overview', {})
        table_data = overview.get('table', [{}])
        if not table_data:
            return {}
            
        league_info = table_data[0].get('data', {})
        rows = league_info.get('table', {}).get('all', [])
        
        formatted_table = []
        for row in rows:
            # Extract form results
            raw_form = row.get('form', [])
            form_results = []
            if isinstance(raw_form, list):
                form_results = [f.get('result', '?') for f in raw_form]
            
            formatted_table.append({
                "rank": row.get("idx"),
                "team": row.get("name"),
                "team_id": row.get("id"),
                "played": row.get("played"),
                "wins": row.get("wins"),
                "draws": row.get("draws"),
                "losses": row.get("losses"),
                "gd": row.get("goalConDiff"),
                "pts": row.get("pts"),
                "form": form_results,
                "deduction": row.get("deductionReason"),
                "is_current": str(row.get('id')) == str(self._team_id)
            })
            
        return {
            "league_name": league_info.get("leagueName"),
            "table": formatted_table
        }

    @property
    def icon(self):
        return "mdi:table-large"
