import logging
from datetime import timedelta, datetime
import requests
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import CONF_NAME
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, CONF_TEAM_ID

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME_PREFIX = "FotMob"

# Update more frequently to support live scores (every 1 minute)
SCAN_INTERVAL = timedelta(minutes=1)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_TEAM_ID): cv.string,
    vol.Optional(CONF_NAME): cv.string,
})

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform from a config entry."""
    team_id = config_entry.data.get(CONF_TEAM_ID)
    name = config_entry.data.get(CONF_NAME)
    
    unique_id = f"fotmob_{team_id}"
    
    async_add_entities([FotMobFixturesSensor(team_id, name, unique_id)], True)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform (Legacy YAML setup)."""
    team_id = config.get(CONF_TEAM_ID)
    name = config.get(CONF_NAME)
    add_entities([FotMobFixturesSensor(team_id, name)], True)

class FotMobFixturesSensor(SensorEntity):
    """Representation of a FotMob Fixtures sensor."""

    def __init__(self, team_id, name, unique_id=None):
        self._team_id = team_id
        self._custom_name = name
        self._name = name or f"{DEFAULT_NAME_PREFIX} {team_id}"
        self._attr_unique_id = unique_id
        self._state = None
        self._attributes = {}
        self._team_name = None

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

    @property
    def icon(self):
        return "mdi:soccer"

    @property
    def entity_picture(self):
        """Return the logo of the tracked team."""
        return f"https://images.fotmob.com/image_resources/logo/teamlogo/{self._team_id}.png"

    def update(self):
        """Fetch new state data for the sensor."""
        url = f"https://www.fotmob.com/api/teams?id={self._team_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                _LOGGER.error("FotMob API returned status code %s for team %s", response.status_code, self._team_id)
                return

            data = response.json()
            
            if not self._team_name:
                self._team_name = data.get('details', {}).get('name')
                if self._team_name and not self._custom_name:
                    self._name = f"{self._team_name}"

            fixtures = data.get('fixtures', {}).get('allFixtures', {}).get('fixtures', [])
            
            active_match = None
            
            # Prioritize matches: 1. Live, 2. Starting, 3. Next Upcoming
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
                home_id = match_to_track.get('home', {}).get('id')
                away_id = match_to_track.get('away', {}).get('id')
                
                is_home = str(home_id) == str(self._team_id)
                opponent = away_team if is_home else home_team
                opponent_id = away_id if is_home else home_id
                
                # Set State: Show score if live, otherwise show match summary
                if status.get('started') and not status.get('finished'):
                    score = status.get('scoreStr', '0 - 0')
                    self._state = f"LIVE: {score}"
                else:
                    self._state = f"{home_team} vs {away_team}"

                self._attributes = {
                    "team_name": self._team_name,
                    "opponent": opponent,
                    "opponent_logo": f"https://images.fotmob.com/image_resources/logo/teamlogo/{opponent_id}.png",
                    "home_away": "Home" if is_home else "Away",
                    "league": match_to_track.get('league', {}).get('name'),
                    "match": f"{home_team} vs {away_team}",
                    "timestamp": status.get('utcTime'),
                    "status": "Live" if (status.get('started') and not status.get('finished')) else "Scheduled",
                    "score": status.get('scoreStr') if status.get('started') else None
                }
            else:
                self._state = "No upcoming matches"
                self._attributes = {"team_name": self._team_name}

        except Exception as e:
            _LOGGER.error("Error updating FotMob sensor for team %s: %s", self._team_id, e)
