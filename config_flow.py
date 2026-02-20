"""Config flow for FotMob Fixtures integration."""
from __future__ import annotations

import logging
from typing import Any

import requests
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, CONF_TEAM_ID

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_TEAM_ID): str,
        vol.Optional("name"): str,
    }
)

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    team_id = data[CONF_TEAM_ID]
    
    # Simple validation: Team ID must be numeric
    if not team_id.isdigit():
         raise InvalidTeam
         
    # Optional: Verify with FotMob API
    url = f"https://www.fotmob.com/api/teams?id={team_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    def fetch():
        return requests.get(url, headers=headers, timeout=10)

    try:
        response = await hass.async_add_executor_job(fetch)
        if response.status_code != 200:
            raise InvalidTeam
        
        team_data = response.json()
        team_name = team_data.get('details', {}).get('name')
        if not team_name:
            raise InvalidTeam
            
        return {"title": team_name}
        
    except Exception as err:
        _LOGGER.error("Error validating FotMob team %s: %s", team_id, err)
        if isinstance(err, InvalidTeam):
            raise err
        raise CannotConnect

class FotMobFixturesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for FotMob Fixtures."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidTeam:
            errors["team_id"] = "invalid_team"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            # Use team name as title if no custom name provided
            title = user_input.get("name") or info["title"]
            return self.async_create_entry(title=title, data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""

class InvalidTeam(HomeAssistantError):
    """Error to indicate there is invalid team ID."""
