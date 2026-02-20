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
        base_url = "https://www.fotmob.com/api/teams?id={self.team_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        async def fetch_tab(tab=None):
            url = f"https://www.fotmob.com/api/teams?id={self.team_id}"
            if tab:
                url += f"&tab={tab}"
            
            response = await self.hass.async_add_executor_job(
                lambda: requests.get(url, headers=headers, timeout=15)
            )
            
            if response.status_code != 200:
                _LOGGER.warning("Error fetching FotMob tab %s: %s", tab or 'overview', response.status_code)
                return {}
            return response.json()

        try:
            # Fetch overview, transfers, and history in parallel (simulated here with async_add_executor_job or sequential for simplicity, but coordinator needs to stay robust)
            # For now, let's fetch them and merge.
            overview = await fetch_tab()
            transfers = await fetch_tab("transfers")
            history = await fetch_tab("history")

            # Merge results
            data = overview
            if transfers:
                data["transfers"] = transfers.get("transfers", {})
            if history:
                data["history"] = history.get("history", {})

            return data

        except Exception as err:
            raise UpdateFailed(f"Unexpected error updating FotMob data: {err}")
