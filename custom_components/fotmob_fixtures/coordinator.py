import logging
import asyncio
from datetime import timedelta

import aiohttp
import async_timeout

from homeassistant.helpers.aiohttp_client import async_get_clientsession
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
        session = async_get_clientsession(self.hass)
        base_url = f"https://www.fotmob.com/api/data/teams?id={self.team_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        async def fetch_json(url):
            try:
                async with async_timeout.timeout(15):
                    response = await session.get(url, headers=headers)
                    if response.status != 200:
                        _LOGGER.warning("Error fetching FotMob URL %s: %s", url, response.status)
                        return {}
                    return await response.json()
            except aiohttp.ClientError as err:
                _LOGGER.error("Network error fetching FotMob URL %s: %s", url, err)
                return {}
            except asyncio.TimeoutError:
                _LOGGER.error("Timeout fetching FotMob URL %s", url)
                return {}
            except Exception as e:
                _LOGGER.error("Unexpected error fetching FotMob URL %s: %s", url, e)
                return {}

        try:
            # 1. Fetch overview first
            overview = await fetch_json(base_url)
            if not overview:
                raise UpdateFailed("Failed to fetch primary team data from FotMob")

            # 2. Discover leagueId for full table data
            league_id = None
            tables = overview.get("table", [])
            if tables:
                league_id = tables[0].get("data", {}).get("leagueId")

            # 3. Fetch secondary data in parallel
            transfers_url = f"{base_url}&tab=transfers"
            history_url = f"{base_url}&tab=history"
            
            # Fetch secondary data in parallel to be efficient
            tasks = [
                fetch_json(transfers_url),
                fetch_json(history_url)
            ]
            
            if league_id:
                tasks.append(fetch_json(f"https://www.fotmob.com/api/leagues?id={league_id}"))
            else:
                tasks.append(asyncio.sleep(0, result={})) # Placeholder

            results = await asyncio.gather(*tasks)
            transfers = results[0]
            history = results[1]
            league_data = results[2]

            # Merge everything
            data = overview
            if transfers:
                data["transfers"] = transfers.get("transfers", {})
            if history:
                data["history"] = history.get("history", {})
            if league_data:
                data["league_table"] = league_data

            return data

        except UpdateFailed:
            raise
        except Exception as err:
            raise UpdateFailed(f"Unexpected error updating FotMob data: {err}")
