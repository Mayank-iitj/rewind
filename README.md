# League of Legends Analytics Agent# Recipe Generation from Food Image



AI-powered analytics agent that uses the League of Legends API to analyze player match history and generate personalized, actionable insights using AWS AI services.This application generates cooking recipes from food images using a transformer-based deep learning model.



## 🎮 Features## Prerequisites



### Core Capabilities- Python 3.8+

- **Comprehensive Match Data Analysis**: Full-year match history analysis via Riot's Match-V5 API- PyTorch 1.13+

- **AI-Powered Insights**: Uses Amazon Bedrock for natural language generation- Flask 2.2+

- **Performance Tracking**: Track win rate, KDA, champion mastery, and trends over time- Pillow, NumPy, and other dependencies in requirements.txt

- **Strengths & Weaknesses**: Identify consistent patterns and areas for improvement

- **Adaptive Coaching Tips**: Personalized recommendations based on gameplay data## Quick Start

- **Year-End Reports**: Creative summaries with highlights and achievements

- **Social Sharing**: Generate shareable visualizations and infographics### Option 1: Local Installation



### Technical Stack1. **Install dependencies**:

- **Backend**: Python Flask REST API   ```

- **Data Processing**: Pandas, NumPy, scikit-learn   pip install -r requirements.txt

- **Visualization**: Plotly, Matplotlib, Seaborn, Pillow   ```

- **AWS Services**: 

  - Amazon Bedrock (AI content generation)2. **Run the application**:

  - Amazon SageMaker (ML predictions - optional)   ```

  - Amazon S3 (storage - optional)   python app.py

- **API Integration**: Riot Games API (Match-V5)   ```

- **Rate Limiting**: Intelligent request throttling and caching   

3. **Access the web interface**:

## 🚀 Quick Start   Open a web browser and go to `http://localhost:5000`



### Prerequisites### Option 2: Docker Deployment

- Python 3.8+

- Riot Games API Key ([Get one here](https://developer.riotgames.com/))1. **Build and run the Docker container**:

- AWS Account (optional, for AI features)   ```

   bash run_docker.sh

### Installation   ```



1. **Install dependencies**:2. **Access the web interface**:

```bash   Open a web browser and go to `http://localhost:5000`

pip install -r requirements.txt

```## Model Weights



2. **Configure environment**:For optimal performance, download the pre-trained model weights and place them in the appropriate locations:

```bash

cp .env.example .env- Model weights: `data/modelbest.ckpt`

```- Ingredient vocabulary: `data/ingr_vocab.pkl`

- Instruction vocabulary: `data/instr_vocab.pkl`

Edit `.env` with your API keys:

```envIf these files are not available, the application will use mock data for demonstration.

RIOT_API_KEY=RGAPI-your-key-here

AWS_ACCESS_KEY_ID=your-aws-key## Production Deployment

AWS_SECRET_ACCESS_KEY=your-aws-secret

```For production deployment, consider:



3. **Run the application**:1. Setting environment variables:

```bash   - `PORT`: The port to run the server on (default: 5000)

python app.py   - `DEBUG`: Enable debug mode (default: False)

```   - `SECRET_KEY`: Flask secret key



4. **Access the web interface**:2. Using Gunicorn as a WSGI server:

Open `http://localhost:5000` in your browser   ```

   gunicorn --config gunicorn.conf.py app:app

## 📖 Usage   ```



### Web Interface3. Setting up SSL for HTTPS support.

1. Enter your Riot ID (Game Name + Tag, e.g., "PlayerName" + "NA1")

2. Click "Generate Insights" to analyze your match history## Environment Variables

3. View comprehensive statistics, champion performance, and coaching tips

4. Generate year-end reports or download social cards to share- `PORT`: Port to run the application (default: 5000)

- `DEBUG`: Enable debug mode (default: False)

### API Examples- `SECRET_KEY`: Secret key for Flask session



#### Health Check## API Endpoints

```bash

curl http://localhost:5000/api/health- `GET /`: Home page

```- `POST /`: Upload and process a food image

- `GET /sample/<name>`: Use a sample image

#### Lookup Player- `GET /health`: Health check endpoint

```bash

curl -X POST http://localhost:5000/api/player/lookup \## License

  -H "Content-Type: application/json" \

  -d '{"game_name": "PlayerName", "tag_line": "NA1"}'MIT License

```

## Acknowledgments

#### Generate Insights

```bashBased on the Recipe Generation from Food Image project, using transformer-based deep learning architecture.
curl -X POST http://localhost:5000/api/player/{puuid}/insights \
  -H "Content-Type: application/json" \
  -d '{"player_name": "PlayerName", "max_matches": 100}'
```

## ⚙️ Configuration

### Key Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `RIOT_API_KEY` | Riot Games API key (required) | - |
| `AWS_REGION` | AWS region | us-east-1 |
| `BEDROCK_MODEL_ID` | Bedrock model ID | claude-3-sonnet |
| `ENABLE_BEDROCK` | Enable AI generation | True |
| `MATCH_HISTORY_LIMIT` | Max matches to analyze | 100 |
| `DEBUG` | Debug mode | False |

See `.env.example` for all available options.

## 🏗️ Architecture

```
recipe_app/
├── app.py                 # Flask application & API endpoints
├── config/
│   └── settings.py        # Configuration management
├── services/
│   ├── riot_api.py        # Riot API client with rate limiting
│   ├── data_processor.py  # Match data extraction & analysis
│   ├── insights_engine.py # Insights & report generation
│   ├── aws_services.py    # AWS Bedrock & SageMaker integration
│   └── visualizations.py  # Charts & infographic generation
├── templates/
│   └── index.html         # Web interface
├── static/js/
│   └── app.js             # Frontend logic
└── requirements.txt       # Python dependencies
```

## 🤖 AWS AI Integration

### Amazon Bedrock
Generates personalized content including:
- Player summaries and year-end reports
- Coaching tips and recommendations
- Motivational messages
- Creative storytelling

### Setup
1. Enable Bedrock in your AWS account
2. Request access to Claude 3 Sonnet model
3. Configure credentials in `.env`
4. Set `ENABLE_BEDROCK=True`

## 🐳 Docker Deployment

### Using Docker Compose
```bash
docker-compose up --build
```

### Manual Docker Build
```bash
docker build -t lol-analytics .
docker run -p 5000:5000 --env-file .env lol-analytics
```

## 📊 Features in Detail

### Performance Dashboard
- Win rate tracking with historical trends
- KDA analysis and champion-specific performance
- Role distribution and preferred positions
- Game time patterns and activity tracking

### AI-Generated Insights
- Personalized strengths identification
- Weakness detection with improvement suggestions
- Adaptive coaching tips that evolve with gameplay
- Creative year-end summaries with storytelling

### Visualizations
- Interactive performance charts
- Champion mastery heatmaps
- Social media-ready cards (1200x630)
- Year-end infographics (Instagram-optimized)

### Social Sharing
- Download beautiful stat cards
- Share on Twitter, Discord, TikTok
- Compare stats with friends
- Generate highlight reels

## 🔒 Privacy & Security

- ✅ On-demand data processing only
- ✅ No permanent player data storage
- ✅ Secure API key management
- ✅ Rate limiting to prevent abuse
- ✅ Optional Redis caching with TTL

## ⚠️ Limitations

- Requires valid Riot API key (rate limited)
- AWS features require AWS account & setup
- Best results with 20+ ranked games
- Historical data limited to 1 year
- Rate limits: 20 req/sec, 100 req/2min

## 🛠️ Development

### Run in Debug Mode
```bash
export DEBUG=True
python app.py
```

### Project Structure
The application follows a modular architecture:
- **Services**: Independent modules for API, data processing, AI, and visualization
- **Config**: Centralized configuration management
- **Templates**: Jinja2 HTML templates
- **Static**: Frontend assets (JS, CSS, images)

## 📝 API Documentation

### Endpoints

#### `GET /api/health`
Health check with feature status

#### `POST /api/player/lookup`
Lookup player by Riot ID
```json
{
  "game_name": "PlayerName",
  "tag_line": "NA1"
}
```

#### `POST /api/player/{puuid}/insights`
Generate comprehensive insights
```json
{
  "player_name": "PlayerName",
  "max_matches": 100,
  "days_back": 365
}
```

#### `POST /api/player/{puuid}/year-end-report`
Generate year-end report
```json
{
  "player_name": "PlayerName"
}
```

#### `POST /api/visualizations/social-card`
Generate shareable social media card

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Riot Games for the League of Legends API
- AWS for AI/ML services
- Open source visualization libraries

---

**Disclaimer**: This project is not affiliated with or endorsed by Riot Games. League of Legends and Riot Games are trademarks of Riot Games, Inc.

**Note**: Developed using AWS AI services (Bedrock) and Riot Games API. Requires appropriate API keys and AWS credentials to function.
