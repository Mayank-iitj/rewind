"""
League of Legends Analytics Agent
AI-powered player insights using AWS services and Riot API
"""
import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
import io

# Import our services
from config.settings import config
from services.riot_api import RiotAPIClient, RiotAPIError
from services.data_processor import MatchDataProcessor
from services.insights_engine import InsightsEngine
from services.visualizations import visualization_generator
from services.aws_services import bedrock_service, sagemaker_service, s3_service

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
CORS(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO if not config.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize services
riot_client = None
insights_engine = InsightsEngine()


def get_riot_client():
    """Get or create Riot API client"""
    global riot_client
    if riot_client is None:
        riot_client = RiotAPIClient()
    return riot_client


# Error handlers
@app.errorhandler(HTTPException)
def handle_http_error(e):
    """Handle HTTP errors"""
    return jsonify({'error': str(e.description)}), e.code


@app.errorhandler(Exception)
def handle_error(e):
    """Handle general errors"""
    logger.error(f"Unexpected error: {e}", exc_info=True)
    return jsonify({'error': 'An unexpected error occurred'}), 500


# Routes
@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'features': {
            'bedrock': bedrock_service.enabled,
            'sagemaker': sagemaker_service.enabled,
            's3': s3_service.enabled,
        }
    })


@app.route('/api/player/lookup', methods=['POST'])
def lookup_player():
    """
    Lookup player by Riot ID
    
    Request body:
    {
        "game_name": "PlayerName",
        "tag_line": "NA1"
    }
    """
    try:
        data = request.get_json()
        game_name = data.get('game_name')
        tag_line = data.get('tag_line')
        
        if not game_name or not tag_line:
            return jsonify({'error': 'game_name and tag_line are required'}), 400
        
        logger.info(f"Looking up player: {game_name}#{tag_line}")
        
        client = get_riot_client()
        account_data = client.get_summoner_by_riot_id(game_name, tag_line)
        
        return jsonify({
            'puuid': account_data.get('puuid'),
            'game_name': account_data.get('gameName'),
            'tag_line': account_data.get('tagLine'),
        })
        
    except RiotAPIError as e:
        logger.error(f"Riot API error: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error looking up player: {e}", exc_info=True)
        return jsonify({'error': 'Failed to lookup player'}), 500


@app.route('/api/player/<puuid>/insights', methods=['POST'])
def generate_insights(puuid: str):
    """
    Generate comprehensive insights for a player
    
    Request body:
    {
        "player_name": "PlayerName",
        "max_matches": 100,
        "days_back": 365
    }
    """
    try:
        data = request.get_json() or {}
        player_name = data.get('player_name', 'Player')
        max_matches = min(int(data.get('max_matches', 100)), config.MATCH_HISTORY_LIMIT)
        days_back = int(data.get('days_back', config.ANALYSIS_LOOKBACK_DAYS))
        
        logger.info(f"Generating insights for {player_name} (PUUID: {puuid})")
        
        # Fetch match history
        client = get_riot_client()
        matches = client.get_full_match_history(puuid, max_matches=max_matches, days_back=days_back)
        
        if not matches:
            return jsonify({'error': 'No match history found'}), 404
        
        # Generate insights
        insights = insights_engine.generate_comprehensive_insights(matches, puuid, player_name)
        
        return jsonify(insights)
        
    except RiotAPIError as e:
        logger.error(f"Riot API error: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error generating insights: {e}", exc_info=True)
        return jsonify({'error': 'Failed to generate insights'}), 500


@app.route('/api/player/<puuid>/year-end-report', methods=['POST'])
def generate_year_end_report(puuid: str):
    """
    Generate year-end report for a player
    
    Request body:
    {
        "player_name": "PlayerName"
    }
    """
    try:
        data = request.get_json() or {}
        player_name = data.get('player_name', 'Player')
        
        logger.info(f"Generating year-end report for {player_name}")
        
        # Fetch full year match history
        client = get_riot_client()
        matches = client.get_full_match_history(puuid, max_matches=200, days_back=365)
        
        if not matches:
            return jsonify({'error': 'No match history found'}), 404
        
        # Generate year-end report
        report = insights_engine.generate_year_end_report(matches, puuid, player_name)
        
        return jsonify(report)
        
    except RiotAPIError as e:
        logger.error(f"Riot API error: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error generating year-end report: {e}", exc_info=True)
        return jsonify({'error': 'Failed to generate year-end report'}), 500


@app.route('/api/visualizations/social-card', methods=['POST'])
def generate_social_card():
    """Generate shareable social media card"""
    try:
        insights = request.get_json()
        
        img_bytes = visualization_generator.create_social_media_card(insights)
        
        return send_file(
            io.BytesIO(img_bytes),
            mimetype='image/jpeg',
            as_attachment=False,
            download_name='social_card.jpg'
        )
        
    except Exception as e:
        logger.error(f"Error generating social card: {e}", exc_info=True)
        return jsonify({'error': 'Failed to generate social card'}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting LoL Analytics Agent on port {port}")
    logger.info(f"Debug mode: {config.DEBUG}")
    logger.info(f"AWS Bedrock enabled: {bedrock_service.enabled}")
    
    app.run(
        host='0.0.0.0' if not config.DEBUG else '127.0.0.1',
        port=port,
        debug=config.DEBUG
    )
