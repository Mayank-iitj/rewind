"""
Riot API Client for League of Legends Match Data
Implements rate limiting, caching, and error handling
"""
import time
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import requests
from ratelimit import limits, sleep_and_retry
from requests.exceptions import RequestException
from config.settings import config

logger = logging.getLogger(__name__)


class RiotAPIError(Exception):
    """Custom exception for Riot API errors"""
    pass


class RiotAPIClient:
    """Client for interacting with Riot Games API"""
    
    BASE_URLS = {
        'americas': 'https://americas.api.riotgames.com',
        'asia': 'https://asia.api.riotgames.com',
        'europe': 'https://europe.api.riotgames.com',
        'sea': 'https://sea.api.riotgames.com',
    }
    
    PLATFORM_URLS = {
        'na1': 'https://na1.api.riotgames.com',
        'euw1': 'https://euw1.api.riotgames.com',
        'eun1': 'https://eun1.api.riotgames.com',
        'kr': 'https://kr.api.riotgames.com',
        'br1': 'https://br1.api.riotgames.com',
        'la1': 'https://la1.api.riotgames.com',
        'la2': 'https://la2.api.riotgames.com',
        'oc1': 'https://oc1.api.riotgames.com',
        'tr1': 'https://tr1.api.riotgames.com',
        'ru': 'https://ru.api.riotgames.com',
        'jp1': 'https://jp1.api.riotgames.com',
        'ph2': 'https://ph2.api.riotgames.com',
        'sg2': 'https://sg2.api.riotgames.com',
        'th2': 'https://th2.api.riotgames.com',
        'tw2': 'https://tw2.api.riotgames.com',
        'vn2': 'https://vn2.api.riotgames.com',
    }
    
    def __init__(self, api_key: Optional[str] = None, region: Optional[str] = None, 
                 platform: Optional[str] = None):
        """
        Initialize Riot API client
        
        Args:
            api_key: Riot API key
            region: Regional routing (americas, asia, europe, sea)
            platform: Platform routing (na1, euw1, etc.)
        """
        self.api_key = api_key or config.RIOT_API_KEY
        self.region = region or config.RIOT_API_REGION
        self.platform = platform or config.RIOT_API_PLATFORM
        
        if not self.api_key:
            raise ValueError("Riot API key is required")
        
        self.regional_base_url = self.BASE_URLS.get(self.region)
        self.platform_base_url = self.PLATFORM_URLS.get(self.platform)
        
        if not self.regional_base_url:
            raise ValueError(f"Invalid region: {self.region}")
        if not self.platform_base_url:
            raise ValueError(f"Invalid platform: {self.platform}")
        
        self.headers = {
            'X-Riot-Token': self.api_key,
            'Accept': 'application/json'
        }
        
        # Cache for API responses
        self._cache = {}
        self._cache_expiry = {}
    
    def _get_from_cache(self, key: str) -> Optional[Dict]:
        """Get data from cache if not expired"""
        if key in self._cache:
            if datetime.now() < self._cache_expiry.get(key, datetime.min):
                return self._cache[key]
            else:
                # Clean expired cache
                del self._cache[key]
                del self._cache_expiry[key]
        return None
    
    def _set_cache(self, key: str, data: Dict, expiry_hours: int = 24):
        """Set data in cache with expiry"""
        self._cache[key] = data
        self._cache_expiry[key] = datetime.now() + timedelta(hours=expiry_hours)
    
    @sleep_and_retry
    @limits(calls=config.RIOT_RATE_LIMIT_PER_SECOND, period=1)
    @limits(calls=config.RIOT_RATE_LIMIT_PER_MINUTE, period=60)
    def _make_request(self, url: str, use_cache: bool = True, 
                     cache_hours: int = 24) -> Dict:
        """
        Make rate-limited request to Riot API
        
        Args:
            url: Full URL to request
            use_cache: Whether to use cache
            cache_hours: Hours to cache the response
            
        Returns:
            JSON response data
        """
        # Check cache
        if use_cache:
            cached = self._get_from_cache(url)
            if cached:
                logger.debug(f"Cache hit for {url}")
                return cached
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Cache successful response
            if use_cache:
                self._set_cache(url, data, cache_hours)
            
            return data
            
        except RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
                if status_code == 404:
                    raise RiotAPIError(f"Resource not found: {url}")
                elif status_code == 403:
                    raise RiotAPIError("Invalid or expired API key")
                elif status_code == 429:
                    raise RiotAPIError("Rate limit exceeded")
                else:
                    raise RiotAPIError(f"API request failed: {status_code}")
            raise RiotAPIError(f"Request error: {str(e)}")
    
    def get_summoner_by_name(self, summoner_name: str) -> Dict:
        """
        Get summoner data by name
        
        Args:
            summoner_name: Summoner name
            
        Returns:
            Summoner data including PUUID
        """
        url = f"{self.platform_base_url}/lol/summoner/v4/summoners/by-name/{summoner_name}"
        return self._make_request(url)
    
    def get_summoner_by_riot_id(self, game_name: str, tag_line: str) -> Dict:
        """
        Get summoner data by Riot ID (Game Name#Tag)
        
        Args:
            game_name: Player's game name
            tag_line: Player's tag line
            
        Returns:
            Account data including PUUID
        """
        url = f"{self.regional_base_url}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        return self._make_request(url)
    
    def get_match_ids_by_puuid(self, puuid: str, start: int = 0, count: int = 100,
                               start_time: Optional[int] = None,
                               end_time: Optional[int] = None,
                               queue: Optional[int] = None) -> List[str]:
        """
        Get match IDs for a player by PUUID
        
        Args:
            puuid: Player's PUUID
            start: Starting index
            count: Number of matches to return (max 100)
            start_time: Epoch timestamp in seconds (optional)
            end_time: Epoch timestamp in seconds (optional)
            queue: Queue ID filter (optional)
            
        Returns:
            List of match IDs
        """
        params = []
        if start:
            params.append(f"start={start}")
        if count:
            params.append(f"count={min(count, 100)}")
        if start_time:
            params.append(f"startTime={start_time}")
        if end_time:
            params.append(f"endTime={end_time}")
        if queue:
            params.append(f"queue={queue}")
        
        query_string = "&".join(params)
        url = f"{self.regional_base_url}/lol/match/v5/matches/by-puuid/{puuid}/ids"
        if query_string:
            url += f"?{query_string}"
        
        return self._make_request(url)
    
    def get_match_details(self, match_id: str) -> Dict:
        """
        Get detailed match data
        
        Args:
            match_id: Match ID
            
        Returns:
            Detailed match data including all participants
        """
        url = f"{self.regional_base_url}/lol/match/v5/matches/{match_id}"
        return self._make_request(url)
    
    def get_match_timeline(self, match_id: str) -> Dict:
        """
        Get match timeline with detailed events
        
        Args:
            match_id: Match ID
            
        Returns:
            Match timeline data
        """
        url = f"{self.regional_base_url}/lol/match/v5/matches/{match_id}/timeline"
        return self._make_request(url)
    
    def get_full_match_history(self, puuid: str, max_matches: int = 100,
                               days_back: int = 365) -> List[Dict]:
        """
        Get full match history for a player
        
        Args:
            puuid: Player's PUUID
            max_matches: Maximum number of matches to retrieve
            days_back: Number of days to look back
            
        Returns:
            List of detailed match data
        """
        # Calculate start time (days back from now)
        start_time = int((datetime.now() - timedelta(days=days_back)).timestamp())
        
        all_matches = []
        start_index = 0
        batch_size = 100
        
        logger.info(f"Fetching match history for PUUID: {puuid}")
        
        while len(all_matches) < max_matches:
            try:
                # Get batch of match IDs
                match_ids = self.get_match_ids_by_puuid(
                    puuid=puuid,
                    start=start_index,
                    count=batch_size,
                    start_time=start_time
                )
                
                if not match_ids:
                    logger.info("No more matches found")
                    break
                
                # Get detailed data for each match
                for match_id in match_ids:
                    if len(all_matches) >= max_matches:
                        break
                    
                    try:
                        match_data = self.get_match_details(match_id)
                        all_matches.append(match_data)
                        logger.debug(f"Retrieved match {len(all_matches)}/{max_matches}")
                    except RiotAPIError as e:
                        logger.warning(f"Failed to get match {match_id}: {e}")
                        continue
                
                start_index += batch_size
                
                # If we got fewer matches than requested, we've reached the end
                if len(match_ids) < batch_size:
                    break
                    
            except RiotAPIError as e:
                logger.error(f"Error fetching match IDs: {e}")
                break
        
        logger.info(f"Retrieved {len(all_matches)} matches total")
        return all_matches
    
    def get_champion_masteries(self, puuid: str) -> List[Dict]:
        """
        Get champion mastery data for a player
        
        Args:
            puuid: Player's PUUID
            
        Returns:
            List of champion mastery data
        """
        url = f"{self.platform_base_url}/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}"
        return self._make_request(url)
