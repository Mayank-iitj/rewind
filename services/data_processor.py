"""
Data Processing Pipeline for Match History Analysis
Extracts, transforms, and analyzes gameplay statistics
"""
import logging
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from collections import defaultdict, Counter
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class MatchDataProcessor:
    """Process and analyze League of Legends match data"""
    
    # Queue IDs for ranked games
    RANKED_SOLO_QUEUE = 420
    RANKED_FLEX_QUEUE = 440
    
    def __init__(self):
        self.processed_data = None
    
    def extract_player_stats(self, match_data: Dict, puuid: str) -> Optional[Dict]:
        """
        Extract a specific player's stats from match data
        
        Args:
            match_data: Full match data from Riot API
            puuid: Player's PUUID to extract stats for
            
        Returns:
            Dictionary of player statistics
        """
        try:
            metadata = match_data.get('metadata', {})
            info = match_data.get('info', {})
            
            # Find the participant
            participants = info.get('participants', [])
            player_data = None
            
            for participant in participants:
                if participant.get('puuid') == puuid:
                    player_data = participant
                    break
            
            if not player_data:
                logger.warning(f"Player {puuid} not found in match")
                return None
            
            # Extract key statistics
            stats = {
                'match_id': metadata.get('matchId'),
                'game_creation': info.get('gameCreation'),
                'game_datetime': datetime.fromtimestamp(info.get('gameCreation', 0) / 1000),
                'game_duration': info.get('gameDuration', 0),
                'queue_id': info.get('queueId'),
                'game_mode': info.get('gameMode'),
                'game_type': info.get('gameType'),
                
                # Player info
                'summoner_name': player_data.get('summonerName'),
                'champion_name': player_data.get('championName'),
                'champion_id': player_data.get('championId'),
                'team_position': player_data.get('teamPosition'),
                'individual_position': player_data.get('individualPosition'),
                'team_id': player_data.get('teamId'),
                
                # Win/Loss
                'win': player_data.get('win'),
                'game_ended_in_surrender': player_data.get('gameEndedInSurrender'),
                'game_ended_in_early_surrender': player_data.get('gameEndedInEarlySurrender'),
                
                # KDA
                'kills': player_data.get('kills', 0),
                'deaths': player_data.get('deaths', 0),
                'assists': player_data.get('assists', 0),
                'kda': self._calculate_kda(
                    player_data.get('kills', 0),
                    player_data.get('deaths', 0),
                    player_data.get('assists', 0)
                ),
                
                # Damage
                'total_damage_dealt': player_data.get('totalDamageDealt', 0),
                'total_damage_dealt_to_champions': player_data.get('totalDamageDealtToChampions', 0),
                'total_damage_taken': player_data.get('totalDamageTaken', 0),
                'physical_damage_dealt_to_champions': player_data.get('physicalDamageDealtToChampions', 0),
                'magic_damage_dealt_to_champions': player_data.get('magicDamageDealtToChampions', 0),
                'true_damage_dealt_to_champions': player_data.get('trueDamageDealtToChampions', 0),
                'total_heal': player_data.get('totalHeal', 0),
                'damage_self_mitigated': player_data.get('damageSelfMitigated', 0),
                
                # Gold & Economy
                'gold_earned': player_data.get('goldEarned', 0),
                'gold_spent': player_data.get('goldSpent', 0),
                'total_minions_killed': player_data.get('totalMinionsKilled', 0),
                'neutral_minions_killed': player_data.get('neutralMinionsKilled', 0),
                'cs_per_minute': self._calculate_cs_per_minute(
                    player_data.get('totalMinionsKilled', 0),
                    player_data.get('neutralMinionsKilled', 0),
                    info.get('gameDuration', 1)
                ),
                
                # Vision
                'vision_score': player_data.get('visionScore', 0),
                'wards_placed': player_data.get('wardsPlaced', 0),
                'wards_killed': player_data.get('wardsKilled', 0),
                'control_wards_placed': player_data.get('detectorWardsPlaced', 0),
                'vision_wards_bought': player_data.get('visionWardsBoughtInGame', 0),
                
                # Objectives
                'turret_kills': player_data.get('turretKills', 0),
                'inhibitor_kills': player_data.get('inhibitorKills', 0),
                'dragon_kills': player_data.get('dragonKills', 0),
                'baron_kills': player_data.get('baronKills', 0),
                'objectives_stolen': player_data.get('objectivesStolen', 0),
                
                # Combat
                'double_kills': player_data.get('doubleKills', 0),
                'triple_kills': player_data.get('tripleKills', 0),
                'quadra_kills': player_data.get('quadraKills', 0),
                'penta_kills': player_data.get('pentaKills', 0),
                'killing_sprees': player_data.get('killingSprees', 0),
                'largest_killing_spree': player_data.get('largestKillingSpree', 0),
                'largest_multi_kill': player_data.get('largestMultiKill', 0),
                
                # Crowd Control
                'total_time_cc_dealt': player_data.get('totalTimeCCDealt', 0),
                'time_ccing_others': player_data.get('timeCCingOthers', 0),
                
                # Items
                'item0': player_data.get('item0', 0),
                'item1': player_data.get('item1', 0),
                'item2': player_data.get('item2', 0),
                'item3': player_data.get('item3', 0),
                'item4': player_data.get('item4', 0),
                'item5': player_data.get('item5', 0),
                'item6': player_data.get('item6', 0),
                
                # First bloods & events
                'first_blood_kill': player_data.get('firstBloodKill', False),
                'first_blood_assist': player_data.get('firstBloodAssist', False),
                'first_tower_kill': player_data.get('firstTowerKill', False),
                'first_tower_assist': player_data.get('firstTowerAssist', False),
                
                # Performance metrics
                'champion_level': player_data.get('champLevel', 0),
                'champion_experience': player_data.get('champExperience', 0),
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error extracting player stats: {e}")
            return None
    
    def process_match_history(self, matches: List[Dict], puuid: str) -> pd.DataFrame:
        """
        Process full match history into structured DataFrame
        
        Args:
            matches: List of match data from Riot API
            puuid: Player's PUUID
            
        Returns:
            DataFrame with processed match statistics
        """
        processed_matches = []
        
        for match in matches:
            stats = self.extract_player_stats(match, puuid)
            if stats:
                processed_matches.append(stats)
        
        if not processed_matches:
            logger.warning("No matches to process")
            return pd.DataFrame()
        
        df = pd.DataFrame(processed_matches)
        
        # Sort by date
        df = df.sort_values('game_datetime', ascending=False)
        
        # Add derived columns
        df['win_numeric'] = df['win'].astype(int)
        df['month'] = df['game_datetime'].dt.to_period('M')
        df['week'] = df['game_datetime'].dt.to_period('W')
        df['day_of_week'] = df['game_datetime'].dt.day_name()
        df['hour_of_day'] = df['game_datetime'].dt.hour
        
        self.processed_data = df
        return df
    
    def calculate_overall_stats(self, df: pd.DataFrame) -> Dict:
        """
        Calculate overall statistics from match history
        
        Args:
            df: Processed match DataFrame
            
        Returns:
            Dictionary of overall statistics
        """
        if df.empty:
            return {}
        
        total_games = len(df)
        wins = df['win'].sum()
        losses = total_games - wins
        
        stats = {
            'total_games': total_games,
            'wins': int(wins),
            'losses': int(losses),
            'win_rate': round(wins / total_games * 100, 2) if total_games > 0 else 0,
            
            # KDA
            'avg_kills': round(df['kills'].mean(), 2),
            'avg_deaths': round(df['deaths'].mean(), 2),
            'avg_assists': round(df['assists'].mean(), 2),
            'avg_kda': round(df['kda'].mean(), 2),
            
            # Damage
            'avg_damage_dealt': round(df['total_damage_dealt_to_champions'].mean(), 0),
            'max_damage_dealt': int(df['total_damage_dealt_to_champions'].max()),
            'avg_damage_taken': round(df['total_damage_taken'].mean(), 0),
            
            # Economy
            'avg_gold_earned': round(df['gold_earned'].mean(), 0),
            'avg_cs': round((df['total_minions_killed'] + df['neutral_minions_killed']).mean(), 1),
            'avg_cs_per_minute': round(df['cs_per_minute'].mean(), 2),
            
            # Vision
            'avg_vision_score': round(df['vision_score'].mean(), 1),
            'avg_wards_placed': round(df['wards_placed'].mean(), 1),
            'avg_control_wards': round(df['control_wards_placed'].mean(), 1),
            
            # Multikills
            'total_double_kills': int(df['double_kills'].sum()),
            'total_triple_kills': int(df['triple_kills'].sum()),
            'total_quadra_kills': int(df['quadra_kills'].sum()),
            'total_penta_kills': int(df['penta_kills'].sum()),
            
            # Game Duration
            'avg_game_duration_minutes': round(df['game_duration'].mean() / 60, 1),
            'total_time_played_hours': round(df['game_duration'].sum() / 3600, 1),
        }
        
        return stats
    
    def get_champion_statistics(self, df: pd.DataFrame, min_games: int = 3) -> pd.DataFrame:
        """
        Get per-champion statistics
        
        Args:
            df: Processed match DataFrame
            min_games: Minimum games required for inclusion
            
        Returns:
            DataFrame with champion statistics
        """
        if df.empty:
            return pd.DataFrame()
        
        champion_stats = df.groupby('champion_name').agg({
            'match_id': 'count',
            'win': ['sum', 'mean'],
            'kills': 'mean',
            'deaths': 'mean',
            'assists': 'mean',
            'kda': 'mean',
            'total_damage_dealt_to_champions': 'mean',
            'gold_earned': 'mean',
            'cs_per_minute': 'mean',
            'vision_score': 'mean',
        }).round(2)
        
        # Flatten column names
        champion_stats.columns = ['games', 'wins', 'win_rate', 'avg_kills', 
                                  'avg_deaths', 'avg_assists', 'avg_kda',
                                  'avg_damage', 'avg_gold', 'avg_cs_per_min', 
                                  'avg_vision_score']
        
        # Convert win_rate to percentage
        champion_stats['win_rate'] = (champion_stats['win_rate'] * 100).round(2)
        
        # Filter by minimum games
        champion_stats = champion_stats[champion_stats['games'] >= min_games]
        
        # Sort by games played
        champion_stats = champion_stats.sort_values('games', ascending=False)
        
        return champion_stats
    
    def get_role_statistics(self, df: pd.DataFrame) -> Dict:
        """
        Get statistics by role/position
        
        Args:
            df: Processed match DataFrame
            
        Returns:
            Dictionary of role statistics
        """
        if df.empty:
            return {}
        
        role_stats = {}
        
        for role in df['team_position'].unique():
            if not role or role == '':
                continue
            
            role_df = df[df['team_position'] == role]
            games = len(role_df)
            
            if games > 0:
                role_stats[role] = {
                    'games': games,
                    'wins': int(role_df['win'].sum()),
                    'win_rate': round(role_df['win'].mean() * 100, 2),
                    'avg_kda': round(role_df['kda'].mean(), 2),
                    'avg_damage': round(role_df['total_damage_dealt_to_champions'].mean(), 0),
                }
        
        return role_stats
    
    def get_performance_trends(self, df: pd.DataFrame, period: str = 'month') -> pd.DataFrame:
        """
        Get performance trends over time
        
        Args:
            df: Processed match DataFrame
            period: Time period for aggregation ('week', 'month')
            
        Returns:
            DataFrame with trend data
        """
        if df.empty:
            return pd.DataFrame()
        
        period_col = period if period in df.columns else 'month'
        
        trends = df.groupby(period_col).agg({
            'match_id': 'count',
            'win': 'mean',
            'kda': 'mean',
            'total_damage_dealt_to_champions': 'mean',
            'gold_earned': 'mean',
            'cs_per_minute': 'mean',
            'vision_score': 'mean',
        }).round(2)
        
        trends.columns = ['games', 'win_rate', 'avg_kda', 'avg_damage', 
                         'avg_gold', 'avg_cs_per_min', 'avg_vision_score']
        trends['win_rate'] = (trends['win_rate'] * 100).round(2)
        
        return trends
    
    def identify_best_champions(self, df: pd.DataFrame, top_n: int = 5) -> List[Dict]:
        """
        Identify player's best performing champions
        
        Args:
            df: Processed match DataFrame
            top_n: Number of top champions to return
            
        Returns:
            List of champion dictionaries sorted by performance
        """
        champion_stats = self.get_champion_statistics(df, min_games=3)
        
        if champion_stats.empty:
            return []
        
        # Score based on win rate and games played
        champion_stats['performance_score'] = (
            champion_stats['win_rate'] * 0.6 + 
            champion_stats['avg_kda'] * 10 * 0.3 +
            np.log1p(champion_stats['games']) * 5 * 0.1
        )
        
        top_champions = champion_stats.nlargest(top_n, 'performance_score')
        
        result = []
        for champion, row in top_champions.iterrows():
            result.append({
                'champion': champion,
                'games': int(row['games']),
                'wins': int(row['wins']),
                'win_rate': row['win_rate'],
                'avg_kda': row['avg_kda'],
                'performance_score': round(row['performance_score'], 2)
            })
        
        return result
    
    def identify_weaknesses(self, df: pd.DataFrame) -> Dict:
        """
        Identify areas for improvement
        
        Args:
            df: Processed match DataFrame
            
        Returns:
            Dictionary of identified weaknesses
        """
        if df.empty:
            return {}
        
        weaknesses = {}
        
        # Check death rate
        avg_deaths = df['deaths'].mean()
        if avg_deaths > 6:
            weaknesses['high_deaths'] = {
                'metric': 'Average Deaths',
                'value': round(avg_deaths, 2),
                'severity': 'high' if avg_deaths > 8 else 'medium',
                'suggestion': 'Focus on positioning and map awareness to reduce deaths'
            }
        
        # Check vision score
        avg_vision = df['vision_score'].mean()
        if avg_vision < 30:
            weaknesses['low_vision'] = {
                'metric': 'Average Vision Score',
                'value': round(avg_vision, 1),
                'severity': 'high' if avg_vision < 20 else 'medium',
                'suggestion': 'Buy more control wards and place trinket wards more frequently'
            }
        
        # Check CS
        avg_cs_per_min = df['cs_per_minute'].mean()
        if avg_cs_per_min < 5:
            weaknesses['low_cs'] = {
                'metric': 'CS per Minute',
                'value': round(avg_cs_per_min, 2),
                'severity': 'medium',
                'suggestion': 'Practice last-hitting and wave management in practice tool'
            }
        
        # Check win rate on losses
        losses = df[df['win'] == False]
        if not losses.empty:
            avg_damage_in_losses = losses['total_damage_dealt_to_champions'].mean()
            overall_avg_damage = df['total_damage_dealt_to_champions'].mean()
            
            if avg_damage_in_losses < overall_avg_damage * 0.7:
                weaknesses['low_damage_in_losses'] = {
                    'metric': 'Damage in Lost Games',
                    'value': round(avg_damage_in_losses, 0),
                    'severity': 'medium',
                    'suggestion': 'Stay more active in teamfights even when behind'
                }
        
        return weaknesses
    
    @staticmethod
    def _calculate_kda(kills: int, deaths: int, assists: int) -> float:
        """Calculate KDA ratio"""
        if deaths == 0:
            return float(kills + assists)
        return round((kills + assists) / deaths, 2)
    
    @staticmethod
    def _calculate_cs_per_minute(minions: int, jungle: int, duration: int) -> float:
        """Calculate CS per minute"""
        total_cs = minions + jungle
        minutes = duration / 60
        if minutes == 0:
            return 0
        return round(total_cs / minutes, 2)
