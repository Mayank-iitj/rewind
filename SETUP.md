# League of Legends Analytics Agent - Setup Guide

## Prerequisites

Before you begin, ensure you have:

1. **Python 3.8+** installed
2. **Riot Games API Key** - [Get one here](https://developer.riotgames.com/)
3. **AWS Account** (optional, for AI features)
   - Amazon Bedrock access (request model access)
   - AWS CLI configured (optional)

## Step-by-Step Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask & Flask-CORS (web framework)
- boto3 (AWS SDK)
- pandas, numpy, scikit-learn (data processing)
- plotly, matplotlib, seaborn, pillow (visualizations)
- requests, ratelimit (API client)

### 2. Configure Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Required - Riot API
RIOT_API_KEY=RGAPI-your-actual-key-here
RIOT_API_REGION=americas
RIOT_API_PLATFORM=na1

# Optional - AWS AI Services
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# Optional - AWS Bedrock
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
ENABLE_BEDROCK=True

# Optional - Feature Flags
ENABLE_SAGEMAKER=False
ENABLE_S3_STORAGE=False
ENABLE_REDIS_CACHE=False
```

### 3. Get Your Riot API Key

1. Go to https://developer.riotgames.com/
2. Sign in with your Riot account
3. Generate a Development API Key
4. Copy the key to your `.env` file

**Note**: Development keys expire after 24 hours. For production, apply for a Production API key.

### 4. Set Up AWS (Optional)

#### For AI-Generated Content:

1. **Create AWS Account**: https://aws.amazon.com/
2. **Request Bedrock Access**:
   - Go to AWS Console → Bedrock
   - Request model access for Claude 3 Sonnet
   - Wait for approval (usually instant)

3. **Create IAM User**:
   ```bash
   # Using AWS CLI
   aws iam create-user --user-name lol-analytics
   aws iam attach-user-policy --user-name lol-analytics --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess
   aws iam create-access-key --user-name lol-analytics
   ```

4. **Copy credentials to `.env`**

### 5. Test Your Setup

Run a quick test:
```bash
python -c "from services.riot_api import RiotAPIClient; print('Riot API OK')"
python -c "from services.aws_services import bedrock_service; print('AWS OK' if bedrock_service.enabled else 'AWS disabled')"
```

### 6. Run the Application

**Development mode**:
```bash
export DEBUG=True  # or set DEBUG=True in PowerShell
python app.py
```

**Production mode with Gunicorn**:
```bash
gunicorn --config gunicorn.conf.py app:app
```

**Access the app**: Open http://localhost:5000

## Docker Deployment

### Quick Start with Docker Compose

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f lol-analytics

# Stop
docker-compose down
```

### Manual Docker Build

```bash
# Build image
docker build -t lol-analytics .

# Run container
docker run -p 5000:5000 --env-file .env lol-analytics
```

## Configuration Options

### Region & Platform Mapping

**Regions** (for routing):
- `americas`: NA, BR, LAN, LAS, OCE
- `asia`: KR, JP
- `europe`: EUW, EUNE, TR, RU
- `sea`: PH, SG, TH, TW, VN

**Platforms** (for summoner lookup):
- `na1`: North America
- `euw1`: EU West
- `eun1`: EU Nordic & East
- `kr`: Korea
- `br1`: Brazil
- `la1`, `la2`: Latin America
- `oc1`: Oceania
- `tr1`: Turkey
- `ru`: Russia
- `jp1`: Japan

### Performance Tuning

**Rate Limiting**:
```env
RIOT_RATE_LIMIT_PER_SECOND=20
RIOT_RATE_LIMIT_PER_MINUTE=100
```

**Analysis Settings**:
```env
MATCH_HISTORY_LIMIT=100
MIN_MATCHES_FOR_INSIGHTS=10
ANALYSIS_LOOKBACK_DAYS=365
```

**Caching**:
```env
CACHE_EXPIRY_HOURS=24
ENABLE_REDIS_CACHE=True
REDIS_HOST=localhost
```

## Troubleshooting

### Common Issues

#### 1. "Import could not be resolved"
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (needs 3.8+)

#### 2. "Invalid or expired API key"
- Verify your Riot API key in `.env`
- Development keys expire after 24 hours
- Check key hasn't been regenerated on dev portal

#### 3. "Rate limit exceeded"
- Wait a few minutes before retrying
- Reduce `MATCH_HISTORY_LIMIT`
- Enable Redis caching to reduce API calls

#### 4. "Bedrock is not enabled"
- Verify AWS credentials in `.env`
- Check Bedrock model access in AWS Console
- Set `ENABLE_BEDROCK=True`

#### 5. "No match history found"
- Player might have no recent games
- Check spelling of game name and tag
- Try different region/platform combination

### Testing Without AWS

The app works without AWS - it will use fallback text generation:

```env
ENABLE_BEDROCK=False
ENABLE_SAGEMAKER=False
ENABLE_S3_STORAGE=False
```

You'll still get all analytics, just without AI-generated summaries.

## Production Checklist

Before deploying to production:

- [ ] Get Production Riot API key
- [ ] Set `DEBUG=False`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure SSL/HTTPS
- [ ] Set up Redis for caching
- [ ] Enable AWS services
- [ ] Configure logging
- [ ] Set up monitoring
- [ ] Configure backup/restore
- [ ] Test rate limiting
- [ ] Review security settings

## Next Steps

1. **Test the API**: Use curl or Postman to test endpoints
2. **Customize visualizations**: Edit `services/visualizations.py`
3. **Add more insights**: Extend `services/insights_engine.py`
4. **Integrate with your app**: Use the REST API
5. **Deploy to cloud**: AWS, GCP, Azure, or Heroku

## Support

For issues or questions:
- Check the main [README.md](README.md)
- Review the [API Documentation](#)
- Open an issue on GitHub

## Resources

- [Riot Games API Docs](https://developer.riotgames.com/docs/lol)
- [AWS Bedrock Docs](https://docs.aws.amazon.com/bedrock/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Plotly Python](https://plotly.com/python/)

Happy analyzing! 🎮📊
