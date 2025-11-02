"""
Insights Engine - Generates comprehensive player insights
Combines statistical analysis with AI-generated content
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd
from services.data_processor import MatchDataProcessor
from services.aws_services import bedrock_service, sagemaker_service

logger = logging.getLogger(__name__)


class InsightsEngine:
    """Generate actionable insights from player data"""
    
    def __init__(self):
        self.processor = MatchDataProcessor()
        self.bedrock = bedrock_service
        self.sagemaker = sagemaker_service
    
    def generate_comprehensive_insights(self, matches: List[Dict], puuid: str,
                                       player_name: str) -> Dict:
        """
        Generate comprehensive insights from match history
        
        Args:
            matches: List of match data
            puuid: Player's PUUID
            player_name: Player's display name
            
        Returns:
            Dictionary containing all insights
        """
        logger.info(f"Generating insights for {player_name}")
        
        # Process match data
        df = self.processor.process_match_history(matches, puuid)
        
        if df.empty:
            return {'error': 'No match data to analyze'}
        
        # Generate various insights
        insights = {
            'player_name': player_name,
            'puuid': puuid,
            'analysis_date': datetime.now().isoformat(),
            'total_matches_analyzed': len(df),
            
            # Overall statistics
            'overall_stats': self.processor.calculate_overall_stats(df),
            
            # Champion analysis
            'champion_stats': self._get_champion_insights(df),
            
            # Role analysis
            'role_stats': self.processor.get_role_statistics(df),
            
            # Performance trends
            'trends': self._get_performance_trends(df),
            
            # Strengths
            'strengths': self._identify_strengths(df),
            
            # Weaknesses
            'weaknesses': self.processor.identify_weaknesses(df),
            
            # Coaching tips
            'coaching_tips': self._generate_coaching_tips(df),
            
            # Playstyle analysis
            'playstyle': self._analyze_playstyle(df),
            
            # Notable achievements
            'achievements': self._identify_achievements(df),
            
            # Recent performance
            'recent_performance': self._analyze_recent_performance(df),
        }
        
        # Add AI-generated summary if enabled
        if self.bedrock.enabled:
            insights['ai_summary'] = self._generate_ai_summary(insights)
        
        return insights
    
    def generate_year_end_report(self, matches: List[Dict], puuid: str,
                                player_name: str) -> Dict:
        """
        Generate special year-end report with creative elements
        
        Args:
            matches: List of match data
            puuid: Player's PUUID
            player_name: Player's display name
            
        Returns:
            Year-end report dictionary
        """
        # Get comprehensive insights first
        insights = self.generate_comprehensive_insights(matches, puuid, player_name)
        
        if 'error' in insights:
            return insights
        
        df = self.processor.processed_data
        
        # Add special year-end sections
        year_end = {
            **insights,
            'report_type': 'year_end_2024',
            
            # Most memorable moments
            'memorable_moments': self._find_memorable_moments(df),
            
            # Monthly progression
            'monthly_progression': self._get_monthly_progression(df),
            
            # Top achievements of the year
            'top_achievements': self._get_top_achievements(df),
            
            # Fun stats
            'fun_stats': self._get_fun_stats(df),
            
            # Comparison to previous periods
            'growth_metrics': self._calculate_growth_metrics(df),
        }
        
        # Generate creative summary
        if self.bedrock.enabled:
            year_end['creative_summary'] = self.bedrock.generate_player_summary(
                {'name': player_name},
                insights['overall_stats']
            )
            
            # Generate motivational message
            best_champ = insights['champion_stats']['best_champions'][0]['champion'] if insights['champion_stats']['best_champions'] else 'Unknown'
            year_end['motivational_message'] = self.bedrock.generate_motivational_message(
                player_name,
                best_champ,
                insights['overall_stats']['win_rate'],
                list(insights['weaknesses'].keys())[0] if insights['weaknesses'] else 'consistency'
            )
        
        return year_end
    
    def _get_champion_insights(self, df: pd.DataFrame) -> Dict:
        """Get detailed champion insights"""
        champion_stats = self.processor.get_champion_statistics(df, min_games=3)
        best_champions = self.processor.identify_best_champions(df, top_n=5)
        
        # Most played
        most_played = df['champion_name'].value_counts().head(10).to_dict()
        
        # Champions with best win rate (min 5 games)
        champ_wr = df.groupby('champion_name').agg({
            'match_id': 'count',
            'win': 'mean'
        })
        champ_wr = champ_wr[champ_wr['match_id'] >= 5]
        champ_wr = champ_wr.sort_values('win', ascending=False)
        highest_wr = {champ: round(wr * 100, 2) for champ, wr in champ_wr['win'].head(5).items()}
        
        return {
            'best_champions': best_champions,
            'most_played': most_played,
            'highest_win_rate': highest_wr,
            'unique_champions_played': df['champion_name'].nunique(),
            'champion_diversity_score': round(df['champion_name'].nunique() / len(df) * 100, 2)
        }
    
    def _get_performance_trends(self, df: pd.DataFrame) -> Dict:
        """Analyze performance trends"""
        monthly = self.processor.get_performance_trends(df, 'month')
        
        # Calculate trend direction
        if len(monthly) >= 2:
            recent_wr = monthly['win_rate'].iloc[-1]
            previous_wr = monthly['win_rate'].iloc[-2]
            wr_trend = 'improving' if recent_wr > previous_wr else 'declining'
            
            recent_kda = monthly['avg_kda'].iloc[-1]
            previous_kda = monthly['avg_kda'].iloc[-2]
            kda_trend = 'improving' if recent_kda > previous_kda else 'declining'
        else:
            wr_trend = 'stable'
            kda_trend = 'stable'
        
        return {
            'monthly_trends': monthly.to_dict() if not monthly.empty else {},
            'win_rate_trend': wr_trend,
            'kda_trend': kda_trend,
            'most_active_month': monthly['games'].idxmax() if not monthly.empty else None,
            'best_performing_month': monthly['win_rate'].idxmax() if not monthly.empty else None,
        }
    
    def _identify_strengths(self, df: pd.DataFrame) -> Dict:
        """Identify player's strengths"""
        strengths = {}
        overall = self.processor.calculate_overall_stats(df)
        
        # High win rate
        if overall['win_rate'] >= 52:
            strengths['win_rate'] = {
                'metric': 'Win Rate',
                'value': overall['win_rate'],
                'description': f"Strong {overall['win_rate']}% win rate shows consistent performance"
            }
        
        # Good KDA
        if overall['avg_kda'] >= 3.0:
            strengths['kda'] = {
                'metric': 'KDA',
                'value': overall['avg_kda'],
                'description': f"Excellent {overall['avg_kda']} KDA demonstrates strong mechanics"
            }
        
        # High vision score
        if overall['avg_vision_score'] >= 35:
            strengths['vision'] = {
                'metric': 'Vision Score',
                'value': overall['avg_vision_score'],
                'description': f"Outstanding vision control with {overall['avg_vision_score']} average score"
            }
        
        # Good CS
        if overall['avg_cs_per_minute'] >= 6:
            strengths['cs'] = {
                'metric': 'CS per Minute',
                'value': overall['avg_cs_per_minute'],
                'description': f"Strong farming with {overall['avg_cs_per_minute']} CS/min"
            }
        
        # Multikills
        if overall['total_penta_kills'] > 0:
            strengths['pentakills'] = {
                'metric': 'Pentakills',
                'value': overall['total_penta_kills'],
                'description': f"Achieved {overall['total_penta_kills']} pentakill(s) this year!"
            }
        
        return strengths
    
    def _generate_coaching_tips(self, df: pd.DataFrame) -> List[str]:
        """Generate personalized coaching tips"""
        weaknesses = self.processor.identify_weaknesses(df)
        champion_stats = self.processor.identify_best_champions(df, top_n=3)
        
        # Recent performance (last 20 games)
        recent_df = df.head(20)
        recent_perf = {
            'win_rate': round(recent_df['win'].mean() * 100, 2),
            'avg_kda': round(recent_df['kda'].mean(), 2)
        }
        
        # Use AI to generate tips if available
        if self.bedrock.enabled:
            tips = self.bedrock.generate_coaching_tips(weaknesses, champion_stats, recent_perf)
            if tips:
                return tips
        
        # Fallback: Generate basic tips
        tips = []
        
        for weakness_key, weakness_data in weaknesses.items():
            tips.append(weakness_data.get('suggestion', ''))
        
        # Add positive reinforcement
        if champion_stats:
            best_champ = champion_stats[0]['champion']
            tips.append(f"Continue mastering {best_champ} - you have a {champion_stats[0]['win_rate']}% win rate!")
        
        return tips[:5]
    
    def _analyze_playstyle(self, df: pd.DataFrame) -> Dict:
        """Analyze player's playstyle"""
        # Calculate playstyle metrics
        avg_damage = df['total_damage_dealt_to_champions'].mean()
        avg_damage_taken = df['total_damage_taken'].mean()
        avg_kills = df['kills'].mean()
        avg_assists = df['assists'].mean()
        
        # Determine playstyle type
        if avg_kills > avg_assists:
            primary_style = 'Aggressive Carry'
        else:
            primary_style = 'Supportive Team Player'
        
        if avg_damage_taken > avg_damage:
            secondary_style = 'Front Line Tank'
        else:
            secondary_style = 'Back Line Damage Dealer'
        
        # Preferred time of day
        time_dist = df['hour_of_day'].value_counts()
        preferred_time = time_dist.idxmax() if not time_dist.empty else None
        
        # Preferred day
        day_dist = df['day_of_week'].value_counts()
        preferred_day = day_dist.idxmax() if not day_dist.empty else None
        
        return {
            'primary_style': primary_style,
            'secondary_style': secondary_style,
            'aggression_score': round(avg_kills / (avg_kills + avg_assists) * 100, 1) if (avg_kills + avg_assists) > 0 else 50,
            'damage_preference': 'Physical' if df['physical_damage_dealt_to_champions'].mean() > df['magic_damage_dealt_to_champions'].mean() else 'Magical',
            'preferred_game_time': f"{preferred_time}:00" if preferred_time else None,
            'preferred_day': preferred_day,
            'avg_game_length_minutes': round(df['game_duration'].mean() / 60, 1),
        }
    
    def _identify_achievements(self, df: pd.DataFrame) -> List[Dict]:
        """Identify notable achievements"""
        achievements = []
        
        # Check for various achievements
        total_pentas = df['penta_kills'].sum()
        if total_pentas > 0:
            achievements.append({
                'title': 'Legendary Pentakill',
                'description': f'Achieved {int(total_pentas)} pentakill(s)!',
                'icon': '🏆',
                'rarity': 'legendary'
            })
        
        total_quadras = df['quadra_kills'].sum()
        if total_quadras >= 5:
            achievements.append({
                'title': 'Quadra Master',
                'description': f'Got {int(total_quadras)} quadra kills',
                'icon': '⭐',
                'rarity': 'epic'
            })
        
        # Win streak
        max_streak = self._calculate_max_streak(df, 'win')
        if max_streak >= 5:
            achievements.append({
                'title': f'{max_streak}-Game Win Streak',
                'description': f'Won {max_streak} games in a row!',
                'icon': '🔥',
                'rarity': 'rare' if max_streak < 10 else 'epic'
            })
        
        # Games played milestone
        total_games = len(df)
        if total_games >= 100:
            achievements.append({
                'title': 'Dedicated Player',
                'description': f'Played {total_games} games this year',
                'icon': '🎮',
                'rarity': 'common'
            })
        
        # High damage game
        max_damage = df['total_damage_dealt_to_champions'].max()
        if max_damage >= 50000:
            achievements.append({
                'title': 'Damage Dealer',
                'description': f'Dealt {int(max_damage):,} damage in a single game',
                'icon': '💥',
                'rarity': 'rare'
            })
        
        return achievements
    
    def _analyze_recent_performance(self, df: pd.DataFrame, games: int = 20) -> Dict:
        """Analyze recent performance"""
        recent_df = df.head(games)
        
        if recent_df.empty:
            return {}
        
        recent_stats = self.processor.calculate_overall_stats(recent_df)
        overall_stats = self.processor.calculate_overall_stats(df)
        
        # Compare to overall
        wr_diff = recent_stats['win_rate'] - overall_stats['win_rate']
        kda_diff = recent_stats['avg_kda'] - overall_stats['avg_kda']
        
        return {
            **recent_stats,
            'games_analyzed': len(recent_df),
            'win_rate_change': round(wr_diff, 2),
            'kda_change': round(kda_diff, 2),
            'trend': 'improving' if wr_diff > 0 else 'declining' if wr_diff < 0 else 'stable'
        }
    
    def _find_memorable_moments(self, df: pd.DataFrame) -> List[Dict]:
        """Find memorable moments from the year"""
        moments = []
        
        # Best game
        best_game_idx = df['kda'].idxmax()
        if pd.notna(best_game_idx):
            best_game = df.loc[best_game_idx]
            moments.append({
                'title': 'Best Game',
                'description': f"{best_game['champion_name']}: {int(best_game['kills'])}/{int(best_game['deaths'])}/{int(best_game['assists'])} KDA",
                'date': best_game['game_datetime'].strftime('%Y-%m-%d'),
                'kda': best_game['kda']
            })
        
        # Highest damage game
        max_dmg_idx = df['total_damage_dealt_to_champions'].idxmax()
        if pd.notna(max_dmg_idx):
            dmg_game = df.loc[max_dmg_idx]
            moments.append({
                'title': 'Highest Damage',
                'description': f"{int(dmg_game['total_damage_dealt_to_champions']):,} damage on {dmg_game['champion_name']}",
                'date': dmg_game['game_datetime'].strftime('%Y-%m-%d'),
                'damage': int(dmg_game['total_damage_dealt_to_champions'])
            })
        
        # First pentakill
        penta_games = df[df['penta_kills'] > 0]
        if not penta_games.empty:
            first_penta = penta_games.iloc[-1]  # Last in sorted desc order = first chronologically
            moments.append({
                'title': 'Pentakill!',
                'description': f"First pentakill on {first_penta['champion_name']}",
                'date': first_penta['game_datetime'].strftime('%Y-%m-%d'),
                'special': True
            })
        
        return moments
    
    def _get_monthly_progression(self, df: pd.DataFrame) -> Dict:
        """Get monthly progression data"""
        monthly = df.groupby('month').agg({
            'match_id': 'count',
            'win': 'mean',
            'kda': 'mean'
        }).round(2)
        
        monthly.columns = ['games', 'win_rate', 'avg_kda']
        monthly['win_rate'] = (monthly['win_rate'] * 100).round(2)
        
        return monthly.to_dict()
    
    def _get_top_achievements(self, df: pd.DataFrame) -> List[str]:
        """Get top achievements summary"""
        achievements = []
        
        stats = self.processor.calculate_overall_stats(df)
        
        if stats['win_rate'] >= 55:
            achievements.append(f"🏆 Elite {stats['win_rate']}% Win Rate")
        
        if stats['total_penta_kills'] > 0:
            achievements.append(f"⚡ {stats['total_penta_kills']} Pentakill(s)")
        
        if stats['total_games'] >= 200:
            achievements.append(f"🎮 {stats['total_games']} Games Played")
        
        if stats['avg_kda'] >= 3.5:
            achievements.append(f"💎 {stats['avg_kda']} Average KDA")
        
        return achievements
    
    def _get_fun_stats(self, df: pd.DataFrame) -> Dict:
        """Generate fun/interesting statistics"""
        return {
            'total_hours_played': round(df['game_duration'].sum() / 3600, 1),
            'total_kills': int(df['kills'].sum()),
            'total_deaths': int(df['deaths'].sum()),
            'total_assists': int(df['assists'].sum()),
            'total_gold_earned': int(df['gold_earned'].sum()),
            'total_minions_slain': int((df['total_minions_killed'] + df['neutral_minions_killed']).sum()),
            'total_wards_placed': int(df['wards_placed'].sum()),
            'favorite_champion': df['champion_name'].mode()[0] if not df.empty else None,
            'longest_game_minutes': round(df['game_duration'].max() / 60, 1),
            'shortest_game_minutes': round(df['game_duration'].min() / 60, 1),
        }
    
    def _calculate_growth_metrics(self, df: pd.DataFrame) -> Dict:
        """Calculate growth metrics comparing periods"""
        if len(df) < 20:
            return {}
        
        # Compare first half vs second half
        midpoint = len(df) // 2
        first_half = df.iloc[midpoint:]  # Older games
        second_half = df.iloc[:midpoint]  # Newer games
        
        first_stats = self.processor.calculate_overall_stats(first_half)
        second_stats = self.processor.calculate_overall_stats(second_half)
        
        return {
            'win_rate_change': round(second_stats['win_rate'] - first_stats['win_rate'], 2),
            'kda_change': round(second_stats['avg_kda'] - first_stats['avg_kda'], 2),
            'damage_change': round(second_stats['avg_damage_dealt'] - first_stats['avg_damage_dealt'], 0),
            'cs_change': round(second_stats['avg_cs_per_minute'] - first_stats['avg_cs_per_minute'], 2),
            'vision_change': round(second_stats['avg_vision_score'] - first_stats['avg_vision_score'], 1),
        }
    
    @staticmethod
    def _calculate_max_streak(df: pd.DataFrame, column: str) -> int:
        """Calculate maximum streak for a boolean column"""
        max_streak = 0
        current_streak = 0
        
        for value in df[column]:
            if value:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak
    
    def _generate_ai_summary(self, insights: Dict) -> str:
        """Generate AI summary of insights"""
        try:
            return self.bedrock.generate_player_summary(
                {'name': insights['player_name']},
                insights['overall_stats']
            )
        except Exception as e:
            logger.error(f"Failed to generate AI summary: {e}")
            return ""
