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
        base_url = f"https://www.fotmob.com/api/teams?id={self.team_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        async def fetch_json(url):
            try:
                response = await self.hass.async_add_executor_job(
                    lambda: requests.get(url, headers=headers, timeout=15)
                )
                if response.status_code != 200:
                    _LOGGER.warning("Error fetching FotMob URL %s: %s", url, response.status_code)
                    return {}
                return response.json()
            except Exception as e:
                _LOGGER.error("Exception fetching FotMob URL %s: %s", url, e)
                return {}

        try:
            # 1. Fetch overview first
            overview = await fetch_json(base_url)
            if not overview:
                return {}

            # 2. Discover leagueId for full table data
            league_id = None
            tables = overview.get("overview", {}).get("table", [])
            if tables:
                league_id = tables[0].get("data", {}).get("leagueId")

            # 3. Fetch secondary data in parallel (transfers, history, league_table)
            transfers = await fetch_json(f"{base_url}&tab=transfers")
            history = await fetch_json(f"{base_url}&tab=history")
            
            league_data = {}
            if league_id:
                league_data = await fetch_json(f"https://www.fotmob.com/api/leagues?id={league_id}")

            # Merge everything
            data = overview
            if transfers:
                data["transfers"] = transfers.get("transfers", {})
            if history:
                data["history"] = history.get("history", {})
            if league_data:
                data["league_table"] = league_data

            return data

        except Exception as err:
            raise UpdateFailed(f"Unexpected error updating FotMob data: {err}")

        except Exception as err:
            raise UpdateFailed(f"Unexpected error updating FotMob data: {err}")
