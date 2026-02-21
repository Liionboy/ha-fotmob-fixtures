import logging
from datetime import datetime
from homeassistant.util import dt as dt_util

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_TEAM_ID

_LOGGER = logging.getLogger(__name__)

def localize_time(utc_time_str):
    """Convert UTC ISO string to local time HH:MM."""
    if not utc_time_str:
        return "N/A"
    try:
        if isinstance(utc_time_str, list) and len(utc_time_str) > 1:
            # Handle list format from nextOpponent [team_id, name, time_str]
            utc_time_str = utc_time_str[1]
        
        utc_dt = dt_util.parse_datetime(utc_time_str)
        if utc_dt:
            from datetime import timezone, timedelta
            gmt2 = timezone(timedelta(hours=2))
            local_dt = utc_dt.astimezone(gmt2)
            return local_dt.strftime("%d/%m/%Y %H:%M GMT+2")
    except Exception:
        pass
    return "N/A"

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
        FotMobTopAssistSensor(coordinator, team_id),
        FotMobTopRatingSensor(coordinator, team_id),
        FotMobTeamTransfersSensor(coordinator, team_id),
        FotMobTeamHistorySensor(coordinator, team_id),
        FotMobLeagueTableSensor(coordinator, team_id),
        FotMobStadiumSensor(coordinator, team_id),
        FotMobCoachSensor(coordinator, team_id),
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

        opponent_rank = "N/A"
        opponent_form = []
        difficulty = "N/A"

        # Try to find opponent in league table
        tables = data.get('overview', {}).get('table', [])
        for table_container in tables:
            rows = table_container.get('data', {}).get('table', {}).get('all', [])
            found_opponent = False
            for row in rows:
                if str(row.get('id')) == str(opponent_id):
                    opponent_rank = row.get('idx')
                    
                    raw_form = table_container.get('teamForm', {}).get(str(opponent_id)) or row.get('form', [])
                    if isinstance(raw_form, list):
                        for f in raw_form:
                            if isinstance(f, dict):
                                opponent_form.append(f.get('resultString', f.get('result', '?')))
                            elif isinstance(f, str):
                                opponent_form.append(f)
                    
                    if isinstance(opponent_rank, int):
                        if opponent_rank <= 4:
                            difficulty = "High"
                        elif opponent_rank <= 10:
                            difficulty = "Medium"
                        else:
                            difficulty = "Low"
                    
                    found_opponent = True
                    break
            if found_opponent:
                break

        attributes = {
            "opponent": opponent,
            "opponent_id": opponent_id,
            "opponent_logo": f"https://images.fotmob.com/image_resources/logo/teamlogo/{opponent_id}.png",
            "home_away": "Home" if is_home else "Away",
            "league": match.get('league', {}).get('name'),
            "match": f"{match.get('home', {}).get('name')} vs {match.get('away', {}).get('name')}",
            "timestamp": localize_time(status.get('utcTime')),
            "status": "Live" if (status.get('started') and not status.get('finished')) else "Scheduled",
            "score": status.get('scoreStr'),
            "opponent_rank": opponent_rank,
            "opponent_form": opponent_form,
            "difficulty": difficulty
        }
        return attributes

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
        # Try league_table first (full API), fallback to overview
        league_data = self.team_data.get('league_table', {})
        tables = league_data.get('table', [])
        if not tables:
            tables = self.team_data.get('overview', {}).get('table', [])

        for table_container in tables:
            # teamForm is at table_container level, NOT inside data.table
            team_form = table_container.get('teamForm', {})
            form_entries = team_form.get(str(self._team_id), [])
            
            if form_entries:
                results = []
                for f in form_entries:
                    if isinstance(f, dict):
                        results.append(f.get('resultString', f.get('result', '?')))
                    elif isinstance(f, str):
                        results.append(f)
                return "-".join(results) if results else "N/A"
            
            # Fallback: check row-level form data
            rows = table_container.get('data', {}).get('table', {}).get('all', [])
            for entry in rows:
                if str(entry.get('id')) == str(self._team_id):
                    form = entry.get('form', [])
                    if isinstance(form, list) and form:
                        return "-".join([f.get('resultString', f.get('result', '?')) if isinstance(f, dict) else str(f) for f in form])
        return "N/A"

    @property
    def extra_state_attributes(self):
        league_data = self.team_data.get('league_table', {})
        tables = league_data.get('table', [])
        if not tables:
            tables = self.team_data.get('overview', {}).get('table', [])

        for table_container in tables:
            team_form = table_container.get('teamForm', {})
            form_entries = team_form.get(str(self._team_id), [])
            
            rows = table_container.get('data', {}).get('table', {}).get('all', [])
            for entry in rows:
                if str(entry.get('id')) == str(self._team_id):
                    return {
                        "form_list": form_entries or entry.get('form', []),
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
        # Prefer overview.topPlayers.byGoals, fallback to squad stats
        players = self.team_data.get('topPlayers', {}).get('byGoals', {}).get('players', [])
        if not players:
             players = self.team_data.get('overview', {}).get('topPlayers', {}).get('byGoals', {}).get('players', [])
        
        if players:
            player = players[0]
            name = player.get('name', 'N/A')
            goals = player.get('stat', {}).get('value', player.get('value', player.get('rank', 0)))
            return f"{name} ({goals} goals)"
        return "N/A"

    @property
    def icon(self):
        return "mdi:star-circle"

class FotMobTopAssistSensor(FotMobBaseSensor):
    """Sensor for top assist provider."""
    entity_description_key = "top_assist"

    @property
    def name(self):
        return f"{self.team_name} Top Assist"

    @property
    def state(self):
        players = self.team_data.get('topPlayers', {}).get('byAssists', {}).get('players', [])
        if not players:
             players = self.team_data.get('overview', {}).get('topPlayers', {}).get('byAssists', {}).get('players', [])

        if players:
            player = players[0]
            name = player.get('name', 'N/A')
            assists = player.get('stat', {}).get('value', player.get('value', player.get('rank', 0)))
            return f"{name} ({assists} assists)"
        return "N/A"

    @property
    def icon(self):
        return "mdi:handshake"

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
        matched_container = None
        for table_container in tables:
            t_data = table_container.get('data', {}).get('table', {})
            current_rows = t_data.get('all', [])
            if any(str(row.get('id')) == str(self._team_id) for row in current_rows):
                league_info = table_container.get('data', {})
                table_data_obj = t_data
                rows = current_rows
                matched_container = table_container
                break
        
        if not rows and tables:
            matched_container = tables[0]
            league_info = matched_container.get('data', {})
            table_data_obj = league_info.get('table', {})
            rows = table_data_obj.get('all', [])
        
        # High-Fidelity Merge: teamForm and nextOpponent are at table_container level
        # (sibling of 'data'), NOT inside data.table
        team_form_map = {}
        team_form_obj = matched_container.get('teamForm', {}) if matched_container else {}
        for t_id, entries in team_form_obj.items():
            team_form_map[str(t_id)] = entries
            
        next_map = {}
        next_obj = matched_container.get('nextOpponent', {}) if matched_container else {}
        if not isinstance(next_obj, dict):
            next_obj = table_data_obj.get('nextOpponent', {})
        if isinstance(next_obj, dict):
            for t_id, data in next_obj.items():
                if isinstance(data, list) and len(data) >= 3:
                    next_map[str(t_id)] = {
                        "id": data[0],
                        "time": localize_time(data[1])
                    }
        
        formatted_table = []
        for row in rows:
            t_id = str(row.get('id'))
            
            # 1. Extract form from teamForm (high-fidelity), fallback to row-local
            form_results = []
            raw_form = team_form_map.get(t_id) or row.get('form', [])
            
            if isinstance(raw_form, list):
                for f in raw_form:
                    if isinstance(f, dict):
                        form_results.append(f.get('resultString', f.get('result', '?')))
                    elif isinstance(f, str):
                        form_results.append(f)
                    else:
                        form_results.append('?')

            # 2. Extract next opponent (prefer merge, fallback to row-local)
            next_data = next_map.get(t_id)
            next_id = next_data.get("id") if isinstance(next_data, dict) else None
            next_time = next_data.get("time") if isinstance(next_data, dict) else "N/A"

            if not next_id:
                next_opponent = row.get("next")
                if isinstance(next_opponent, list) and len(next_opponent) > 0:
                    next_id = next_opponent[0].get("id")
                    # Fallback time extraction if needed
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
                "timestamp": next_time,
                "color": row.get("qualColor") or row.get("color") or "", 
                "deduction": row.get("deductionReason"),
                "is_current": t_id == str(self._team_id)
            })
            
        return {
            "league_name": league_info.get("leagueName", "N/A"),
            "table": formatted_table
        }

class FotMobStadiumSensor(FotMobBaseSensor):
    """Sensor for team stadium."""
    entity_description_key = "stadium"

    @property
    def name(self):
        return f"{self.team_name} Stadium"

    @property
    def state(self):
        details = self.team_data.get('details', {})
        stadium = details.get('stadium')
        if not stadium:
            stadium = details.get('sportsTeamJSONLD', {}).get('location', {}).get('name')
        if not stadium:
            stadium = details.get('location', {}).get('name')
        if not stadium:
            stadium = details.get('venue', {}).get('name', 'N/A')
            
        return stadium if isinstance(stadium, str) else stadium.get('name', 'N/A')

    @property
    def extra_state_attributes(self):
        details = self.team_data.get('details', {})
        location = details.get('sportsTeamJSONLD', {}).get('location', {})
        if not location:
            location = details.get('location', {})
            
        city = location.get('address', {}).get('addressLocality', 'N/A')
        country = location.get('address', {}).get('addressCountry', 'N/A')
        
        capacity = "N/A"
        faq = details.get('faqJSONLD', {}).get('mainEntity', [])
        for q in faq:
            if 'capacity' in q.get('name', '').lower():
                answer = q.get('acceptedAnswer', {}).get('text', '')
                import re
                match = re.search(r'\b\d{4,6}\b', answer)
                if match:
                    capacity = match.group(0)
                break

        return {
            "city": city,
            "country": country,
            "lat": location.get('geo', {}).get('latitude'),
            "lon": location.get('geo', {}).get('longitude'),
            "capacity": capacity
        }

    @property
    def icon(self):
        return "mdi:stadium"

class FotMobCoachSensor(FotMobBaseSensor):
    """Sensor for team coach."""
    entity_description_key = "coach"

    @property
    def name(self):
        return f"{self.team_name} Coach"

    @property
    def state(self):
        coach = self.team_data.get('coach', {})
        if not coach:
            coach = self.team_data.get('overview', {}).get('coach', {})
            
        if isinstance(coach, list) and len(coach) > 0 and isinstance(coach[0], list):
            for group in coach:
                if isinstance(group, list) and len(group) == 2 and group[0] == 'Coach':
                    if isinstance(group[1], list) and len(group[1]) > 0:
                        return group[1][0].get('name', 'N/A')

        if isinstance(coach, dict) and coach.get('name'):
            return coach.get('name', 'N/A')
            
        # Fallback to squad iteration
        squad_list = self.team_data.get('squad', {}).get('squad', [])
        for group in squad_list:
            if isinstance(group, dict) and str(group.get('title', '')).lower() == "coach":
                members = group.get('members', [])
                if members and isinstance(members, list) and len(members) > 0:
                    coach_name = members[0].get('name')
                    if coach_name:
                        return coach_name

        return "N/A"

    @property
    def extra_state_attributes(self):
        coach = self.team_data.get('coach', {}) or self.team_data.get('overview', {}).get('coach', {})
        
        if isinstance(coach, dict) and coach.get('name'):
            return {
                "age": coach.get('age', 'N/A'),
                "country": coach.get('countryName', 'N/A'),
            }
            
        # Fallback to squad iteration
        squad_list = self.team_data.get('squad', {}).get('squad', [])
        for group in squad_list:
            if isinstance(group, dict) and str(group.get('title', '')).lower() == "coach":
                members = group.get('members', [])
                if members and isinstance(members, list) and len(members) > 0:
                    coach_dict = members[0]
                    return {
                        "age": coach_dict.get('age', 'N/A'),
                        "country": coach_dict.get('countryName', 'N/A'),
                    }
                    
        return {
            "age": "N/A",
            "country": "N/A",
        }

    @property
    def icon(self):
        return "mdi:account-tie"
