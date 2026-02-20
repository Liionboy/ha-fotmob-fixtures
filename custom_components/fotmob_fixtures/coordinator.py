import logging
import async_timeout
import requests
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

class FotMobDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching FotMob data."""

    def __init__(self, hass, team_id):
        """Initialize the coordinator."""
        self.team_id = team_id
        super().__init__(
            hass,
            _LOGGER,
            name=f"FotMob Team {team_id}",
            update_interval=timedelta(minutes=1),
        )

    async def _async_update_data(self):
        """Fetch data from FotMob API."""
        url = f"https://www.fotmob.com/api/teams?id={self.team_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        try:
            # We use hass.async_add_executor_job to run the blocking requests.get in a thread
            response = await self.hass.async_add_executor_job(
                lambda: requests.get(url, headers=headers, timeout=15)
            )
            
            if response.status_code != 200:
                raise UpdateFailed(f"Error communicating with FotMob API: {response.status_code}")

            return response.json()

        except Exception as err:
            raise UpdateFailed(f"Unexpected error updating FotMob data: {err}")
