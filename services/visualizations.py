"""
Visualization Generator
Creates charts, graphs, and social media-ready images
"""
import io
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import seaborn as sns

logger = logging.getLogger(__name__)


class VisualizationGenerator:
    """Generate visualizations from player data"""
    
    # Color schemes
    COLORS = {
        'primary': '#0C1821',
        'secondary': '#1B2A41',
        'accent': '#C1292E',
        'win': '#4CAF50',
        'loss': '#F44336',
        'gold': '#FFD700',
        'silver': '#C0C0C0',
        'bronze': '#CD7F32',
    }
    
    def __init__(self):
        """Initialize visualization generator"""
        sns.set_theme(style='darkgrid')
        plt.style.use('dark_background')
    
    def create_performance_dashboard(self, insights: Dict) -> bytes:
        """
        Create comprehensive performance dashboard
        
        Args:
            insights: Player insights dictionary
            
        Returns:
            PNG image bytes
        """
        try:
            stats = insights.get('overall_stats', {})
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Win Rate', 'KDA Ratio', 'Average Damage', 'Vision Score'),
                specs=[[{'type': 'indicator'}, {'type': 'indicator'}],
                       [{'type': 'indicator'}, {'type': 'indicator'}]]
            )
            
            # Win Rate gauge
            fig.add_trace(go.Indicator(
                mode="gauge+number+delta",
                value=stats.get('win_rate', 0),
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Win Rate (%)"},
                delta={'reference': 50},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': self.COLORS['win']},
                    'steps': [
                        {'range': [0, 45], 'color': "lightgray"},
                        {'range': [45, 50], 'color': "gray"},
                        {'range': [50, 55], 'color': "lightgreen"},
                        {'range': [55, 100], 'color': self.COLORS['win']}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 50
                    }
                }
            ), row=1, col=1)
            
            # KDA indicator
            fig.add_trace(go.Indicator(
                mode="number+delta",
                value=stats.get('avg_kda', 0),
                title={'text': "Avg KDA"},
                delta={'reference': 2.0, 'relative': False},
                domain={'x': [0, 1], 'y': [0, 1]}
            ), row=1, col=2)
            
            # Damage indicator
            fig.add_trace(go.Indicator(
                mode="number",
                value=stats.get('avg_damage_dealt', 0),
                title={'text': "Avg Damage"},
                number={'suffix': "", 'valueformat': ',.0f'},
                domain={'x': [0, 1], 'y': [0, 1]}
            ), row=2, col=1)
            
            # Vision indicator
            fig.add_trace(go.Indicator(
                mode="number+delta",
                value=stats.get('avg_vision_score', 0),
                title={'text': "Avg Vision"},
                delta={'reference': 30, 'relative': False},
                domain={'x': [0, 1], 'y': [0, 1]}
            ), row=2, col=2)
            
            fig.update_layout(
                title=f"Performance Dashboard - {insights.get('player_name', 'Player')}",
                height=600,
                showlegend=False,
                paper_bgcolor=self.COLORS['primary'],
                font={'color': 'white', 'size': 14}
            )
            
            return fig.to_image(format='png')
            
        except Exception as e:
            logger.error(f"Error creating performance dashboard: {e}")
            return self._create_error_image("Failed to create dashboard")
    
    def create_champion_chart(self, champion_stats: Dict) -> bytes:
        """
        Create champion performance chart
        
        Args:
            champion_stats: Champion statistics dictionary
            
        Returns:
            PNG image bytes
        """
        try:
            best_champions = champion_stats.get('best_champions', [])
            
            if not best_champions:
                return self._create_error_image("No champion data available")
            
            # Prepare data
            champions = [c['champion'] for c in best_champions]
            games = [c['games'] for c in best_champions]
            win_rates = [c['win_rate'] for c in best_champions]
            kdas = [c['avg_kda'] for c in best_champions]
            
            # Create figure with secondary y-axis
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Add bar chart for games
            fig.add_trace(
                go.Bar(name='Games Played', x=champions, y=games, marker_color=self.COLORS['secondary']),
                secondary_y=False,
            )
            
            # Add line chart for win rate
            fig.add_trace(
                go.Scatter(name='Win Rate %', x=champions, y=win_rates, 
                          marker_color=self.COLORS['win'], line=dict(width=3)),
                secondary_y=True,
            )
            
            # Add line chart for KDA
            fig.add_trace(
                go.Scatter(name='Avg KDA', x=champions, y=kdas, 
                          marker_color=self.COLORS['gold'], line=dict(width=3, dash='dash')),
                secondary_y=True,
            )
            
            # Update layout
            fig.update_layout(
                title='Top Champions Performance',
                xaxis_title='Champion',
                height=500,
                paper_bgcolor=self.COLORS['primary'],
                plot_bgcolor=self.COLORS['secondary'],
                font={'color': 'white'},
                hovermode='x unified'
            )
            
            fig.update_yaxes(title_text="Games Played", secondary_y=False)
            fig.update_yaxes(title_text="Win Rate % / KDA", secondary_y=True)
            
            return fig.to_image(format='png')
            
        except Exception as e:
            logger.error(f"Error creating champion chart: {e}")
            return self._create_error_image("Failed to create champion chart")
    
    def create_trend_chart(self, trends: Dict) -> bytes:
        """
        Create performance trend chart
        
        Args:
            trends: Trend data dictionary
            
        Returns:
            PNG image bytes
        """
        try:
            monthly_trends = trends.get('monthly_trends', {})
            
            if not monthly_trends:
                return self._create_error_image("No trend data available")
            
            # Convert to DataFrame
            df = pd.DataFrame(monthly_trends).T
            df.index = df.index.astype(str)
            
            # Create figure
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Win Rate Over Time', 'Performance Metrics'),
                vertical_spacing=0.12
            )
            
            # Win rate trend
            fig.add_trace(
                go.Scatter(x=df.index, y=df['win_rate'], name='Win Rate %',
                          fill='tozeroy', line=dict(color=self.COLORS['win'], width=3)),
                row=1, col=1
            )
            
            # Performance metrics
            fig.add_trace(
                go.Scatter(x=df.index, y=df['avg_kda'], name='Avg KDA',
                          line=dict(color=self.COLORS['gold'], width=2)),
                row=2, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=df.index, y=df['avg_vision_score'], name='Vision Score',
                          line=dict(color='cyan', width=2)),
                row=2, col=1
            )
            
            # Update layout
            fig.update_layout(
                title='Performance Trends',
                height=600,
                paper_bgcolor=self.COLORS['primary'],
                plot_bgcolor=self.COLORS['secondary'],
                font={'color': 'white'},
                showlegend=True,
                hovermode='x unified'
            )
            
            fig.update_xaxes(title_text="Month", row=2, col=1)
            fig.update_yaxes(title_text="Win Rate %", row=1, col=1)
            fig.update_yaxes(title_text="Value", row=2, col=1)
            
            return fig.to_image(format='png')
            
        except Exception as e:
            logger.error(f"Error creating trend chart: {e}")
            return self._create_error_image("Failed to create trend chart")
    
    def create_role_distribution_chart(self, role_stats: Dict) -> bytes:
        """
        Create role distribution pie chart
        
        Args:
            role_stats: Role statistics dictionary
            
        Returns:
            PNG image bytes
        """
        try:
            if not role_stats:
                return self._create_error_image("No role data available")
            
            roles = list(role_stats.keys())
            games = [stats['games'] for stats in role_stats.values()]
            win_rates = [stats['win_rate'] for stats in role_stats.values()]
            
            # Create pie chart
            fig = go.Figure()
            
            fig.add_trace(go.Pie(
                labels=roles,
                values=games,
                hole=0.4,
                marker=dict(colors=px.colors.qualitative.Set3),
                text=win_rates,
                texttemplate='%{label}<br>%{text:.1f}% WR',
                hovertemplate='<b>%{label}</b><br>Games: %{value}<br>Win Rate: %{text:.1f}%<extra></extra>'
            ))
            
            fig.update_layout(
                title='Role Distribution & Win Rates',
                height=500,
                paper_bgcolor=self.COLORS['primary'],
                font={'color': 'white', 'size': 12},
                showlegend=True
            )
            
            return fig.to_image(format='png')
            
        except Exception as e:
            logger.error(f"Error creating role chart: {e}")
            return self._create_error_image("Failed to create role chart")
    
    def create_social_media_card(self, insights: Dict) -> bytes:
        """
        Create shareable social media card
        
        Args:
            insights: Player insights dictionary
            
        Returns:
            JPEG image bytes
        """
        try:
            # Create image
            width, height = 1200, 630
            img = Image.new('RGB', (width, height), color=self.COLORS['primary'])
            draw = ImageDraw.Draw(img)
            
            # Try to load fonts
            try:
                title_font = ImageFont.truetype("arial.ttf", 60)
                stat_font = ImageFont.truetype("arial.ttf", 40)
                label_font = ImageFont.truetype("arial.ttf", 28)
            except:
                title_font = ImageFont.load_default()
                stat_font = ImageFont.load_default()
                label_font = ImageFont.load_default()
            
            stats = insights.get('overall_stats', {})
            player_name = insights.get('player_name', 'Player')
            
            # Title
            title = f"{player_name}'s 2024 Season"
            draw.text((width//2, 80), title, fill='white', font=title_font, anchor='mm')
            
            # Divider line
            draw.line([(100, 150), (width-100, 150)], fill=self.COLORS['accent'], width=3)
            
            # Stats layout
            col1_x = width // 4
            col2_x = width // 2
            col3_x = 3 * width // 4
            row1_y = 250
            row2_y = 420
            
            # Stat 1: Win Rate
            self._draw_stat(draw, col1_x, row1_y, 
                          f"{stats.get('win_rate', 0):.1f}%", 
                          "WIN RATE", stat_font, label_font)
            
            # Stat 2: KDA
            self._draw_stat(draw, col2_x, row1_y,
                          f"{stats.get('avg_kda', 0):.2f}",
                          "AVG KDA", stat_font, label_font)
            
            # Stat 3: Games
            self._draw_stat(draw, col3_x, row1_y,
                          str(stats.get('total_games', 0)),
                          "TOTAL GAMES", stat_font, label_font)
            
            # Stat 4: Pentakills
            self._draw_stat(draw, col1_x, row2_y,
                          str(stats.get('total_penta_kills', 0)),
                          "PENTAKILLS", stat_font, label_font)
            
            # Stat 5: Hours Played
            self._draw_stat(draw, col2_x, row2_y,
                          f"{stats.get('total_time_played_hours', 0):.0f}h",
                          "TIME PLAYED", stat_font, label_font)
            
            # Stat 6: Damage
            damage = stats.get('avg_damage_dealt', 0)
            damage_k = f"{damage/1000:.1f}k" if damage >= 1000 else str(int(damage))
            self._draw_stat(draw, col3_x, row2_y,
                          damage_k,
                          "AVG DAMAGE", stat_font, label_font)
            
            # Footer
            footer = "Generated by LoL Analytics Agent"
            draw.text((width//2, height-40), footer, fill='gray', font=label_font, anchor='mm')
            
            # Convert to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG', quality=95)
            img_bytes.seek(0)
            
            return img_bytes.getvalue()
            
        except Exception as e:
            logger.error(f"Error creating social media card: {e}")
            return self._create_error_image("Failed to create social card", format='JPEG')
    
    def create_year_end_infographic(self, year_end_report: Dict) -> bytes:
        """
        Create comprehensive year-end infographic
        
        Args:
            year_end_report: Year-end report dictionary
            
        Returns:
            PNG image bytes
        """
        try:
            # Create a multi-section infographic
            width, height = 1080, 1920
            img = Image.new('RGB', (width, height), color=self.COLORS['primary'])
            draw = ImageDraw.Draw(img)
            
            # Load fonts
            try:
                title_font = ImageFont.truetype("arial.ttf", 70)
                heading_font = ImageFont.truetype("arial.ttf", 50)
                stat_font = ImageFont.truetype("arial.ttf", 45)
                label_font = ImageFont.truetype("arial.ttf", 32)
            except:
                title_font = ImageFont.load_default()
                heading_font = ImageFont.load_default()
                stat_font = ImageFont.load_default()
                label_font = ImageFont.load_default()
            
            player_name = year_end_report.get('player_name', 'Player')
            stats = year_end_report.get('overall_stats', {})
            fun_stats = year_end_report.get('fun_stats', {})
            achievements = year_end_report.get('achievements', [])
            
            y_pos = 80
            
            # Header
            draw.text((width//2, y_pos), f"{player_name}", 
                     fill='white', font=title_font, anchor='mm')
            y_pos += 80
            draw.text((width//2, y_pos), "2024 YEAR IN REVIEW", 
                     fill=self.COLORS['gold'], font=heading_font, anchor='mm')
            y_pos += 100
            
            # Section 1: Key Stats
            draw.text((width//2, y_pos), "KEY STATISTICS", 
                     fill=self.COLORS['accent'], font=heading_font, anchor='mm')
            y_pos += 80
            
            key_stats = [
                (f"{stats.get('total_games', 0)} GAMES", "PLAYED"),
                (f"{stats.get('win_rate', 0):.1f}%", "WIN RATE"),
                (f"{stats.get('avg_kda', 0):.2f}", "AVG KDA"),
                (f"{fun_stats.get('total_hours_played', 0):.0f}H", "TIME INVESTED")
            ]
            
            for i, (value, label) in enumerate(key_stats):
                if i % 2 == 0:
                    x = width // 3
                else:
                    x = 2 * width // 3
                
                draw.text((x, y_pos), value, fill=self.COLORS['gold'], 
                         font=stat_font, anchor='mm')
                draw.text((x, y_pos + 40), label, fill='lightgray', 
                         font=label_font, anchor='mm')
                
                if i % 2 == 1:
                    y_pos += 120
            
            y_pos += 60
            
            # Section 2: Achievements
            if achievements:
                draw.text((width//2, y_pos), "TOP ACHIEVEMENTS", 
                         fill=self.COLORS['accent'], font=heading_font, anchor='mm')
                y_pos += 70
                
                for achievement in achievements[:3]:
                    icon = achievement.get('icon', '⭐')
                    title = achievement.get('title', '')
                    desc = achievement.get('description', '')
                    
                    draw.text((120, y_pos), icon, fill='white', font=stat_font)
                    draw.text((200, y_pos), title, fill='white', font=label_font)
                    draw.text((200, y_pos + 35), desc, fill='gray', font=label_font)
                    y_pos += 100
            
            y_pos += 40
            
            # Section 3: Fun Stats
            draw.text((width//2, y_pos), "FUN FACTS", 
                     fill=self.COLORS['accent'], font=heading_font, anchor='mm')
            y_pos += 70
            
            fun_facts = [
                f"💀 {fun_stats.get('total_deaths', 0):,} Total Deaths",
                f"🎯 {fun_stats.get('total_kills', 0):,} Total Kills",
                f"🤝 {fun_stats.get('total_assists', 0):,} Total Assists",
                f"💰 {fun_stats.get('total_gold_earned', 0):,} Gold Earned",
                f"👁️ {fun_stats.get('total_wards_placed', 0):,} Wards Placed",
            ]
            
            for fact in fun_facts:
                draw.text((width//2, y_pos), fact, fill='white', 
                         font=label_font, anchor='mm')
                y_pos += 50
            
            # Footer
            draw.text((width//2, height-60), "Share your stats!", 
                     fill='gray', font=label_font, anchor='mm')
            draw.text((width//2, height-25), "#LoLWrapped2024", 
                     fill=self.COLORS['accent'], font=label_font, anchor='mm')
            
            # Convert to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            return img_bytes.getvalue()
            
        except Exception as e:
            logger.error(f"Error creating year-end infographic: {e}")
            return self._create_error_image("Failed to create infographic")
    
    def _draw_stat(self, draw: ImageDraw.Draw, x: int, y: int, 
                   value: str, label: str, stat_font, label_font):
        """Helper to draw a centered stat with label"""
        draw.text((x, y), value, fill=self.COLORS['gold'], 
                 font=stat_font, anchor='mm')
        draw.text((x, y + 50), label, fill='lightgray', 
                 font=label_font, anchor='mm')
    
    def _create_error_image(self, message: str, format: str = 'PNG') -> bytes:
        """Create simple error image"""
        img = Image.new('RGB', (800, 400), color=self.COLORS['primary'])
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 32)
        except:
            font = ImageFont.load_default()
        
        draw.text((400, 200), message, fill='white', font=font, anchor='mm')
        
        img_bytes = io.BytesIO()
        img.save(img_bytes, format=format)
        img_bytes.seek(0)
        
        return img_bytes.getvalue()


# Singleton instance
visualization_generator = VisualizationGenerator()
