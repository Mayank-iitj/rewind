# API Documentation

## Base URL
```
http://localhost:5000
```

## Authentication
Most endpoints don't require authentication, but you must configure your Riot API key in the `.env` file.

---

## Endpoints

### Health Check
Check if the service is running and view enabled features.

**Endpoint:** `GET /api/health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-11-02T10:30:00",
  "features": {
    "bedrock": true,
    "sagemaker": false,
    "s3": false
  }
}
```

---

### Lookup Player
Lookup a player's account by Riot ID to get their PUUID.

**Endpoint:** `POST /api/player/lookup`

**Request Body:**
```json
{
  "game_name": "Faker",
  "tag_line": "KR1"
}
```

**Response:**
```json
{
  "puuid": "abc123...",
  "game_name": "Faker",
  "tag_line": "KR1"
}
```

**Error Codes:**
- `400`: Missing required fields or player not found
- `500`: Server error

---

### Generate Insights
Generate comprehensive insights from a player's match history.

**Endpoint:** `POST /api/player/{puuid}/insights`

**Parameters:**
- `puuid` (path): Player's PUUID from lookup endpoint

**Request Body:**
```json
{
  "player_name": "Faker",
  "max_matches": 100,
  "days_back": 365
}
```

**Query Parameters:**
- `max_matches` (optional): Number of matches to analyze (default: 100, max: 100)
- `days_back` (optional): Days to look back (default: 365)

**Response:**
```json
{
  "player_name": "Faker",
  "puuid": "abc123...",
  "analysis_date": "2024-11-02T10:30:00",
  "total_matches_analyzed": 100,
  
  "overall_stats": {
    "total_games": 100,
    "wins": 65,
    "losses": 35,
    "win_rate": 65.0,
    "avg_kills": 8.5,
    "avg_deaths": 3.2,
    "avg_assists": 7.8,
    "avg_kda": 5.09,
    "avg_damage_dealt": 25000,
    "avg_gold_earned": 12500,
    "avg_cs_per_minute": 8.5,
    "avg_vision_score": 35.2,
    "total_time_played_hours": 50.5
  },
  
  "champion_stats": {
    "best_champions": [
      {
        "champion": "Azir",
        "games": 15,
        "wins": 12,
        "win_rate": 80.0,
        "avg_kda": 6.5,
        "performance_score": 85.2
      }
    ],
    "most_played": {
      "Azir": 15,
      "LeBlanc": 12,
      "Zed": 10
    },
    "unique_champions_played": 25,
    "champion_diversity_score": 25.0
  },
  
  "role_stats": {
    "MIDDLE": {
      "games": 80,
      "wins": 52,
      "win_rate": 65.0,
      "avg_kda": 5.2,
      "avg_damage": 26000
    }
  },
  
  "trends": {
    "monthly_trends": {...},
    "win_rate_trend": "improving",
    "kda_trend": "improving"
  },
  
  "strengths": {
    "kda": {
      "metric": "KDA",
      "value": 5.09,
      "description": "Excellent 5.09 KDA demonstrates strong mechanics"
    }
  },
  
  "weaknesses": {
    "low_vision": {
      "metric": "Average Vision Score",
      "value": 28.5,
      "severity": "medium",
      "suggestion": "Buy more control wards and place trinket wards more frequently"
    }
  },
  
  "coaching_tips": [
    "Focus on maintaining high CS per minute in losing games",
    "Continue mastering Azir - you have a 80% win rate!",
    "Improve vision score by placing 2-3 more wards per game"
  ],
  
  "playstyle": {
    "primary_style": "Aggressive Carry",
    "aggression_score": 72.5,
    "damage_preference": "Magical",
    "preferred_day": "Saturday",
    "avg_game_length_minutes": 28.5
  },
  
  "achievements": [
    {
      "title": "Pentakill Master",
      "description": "Achieved 2 pentakills!",
      "icon": "🏆",
      "rarity": "legendary"
    }
  ],
  
  "recent_performance": {
    "games_analyzed": 20,
    "win_rate": 70.0,
    "avg_kda": 5.8,
    "win_rate_change": 5.0,
    "trend": "improving"
  }
}
```

**Error Codes:**
- `400`: Invalid PUUID or parameters
- `404`: No match history found
- `500`: Server error

---

### Generate Year-End Report
Generate a special year-end report with creative elements.

**Endpoint:** `POST /api/player/{puuid}/year-end-report`

**Parameters:**
- `puuid` (path): Player's PUUID

**Request Body:**
```json
{
  "player_name": "Faker"
}
```

**Response:**
Extends the insights response with additional fields:
```json
{
  ...all insights fields...,
  "report_type": "year_end_2024",
  
  "memorable_moments": [
    {
      "title": "Best Game",
      "description": "Azir: 15/2/10 KDA",
      "date": "2024-08-15",
      "kda": 12.5
    }
  ],
  
  "monthly_progression": {...},
  
  "fun_stats": {
    "total_hours_played": 50.5,
    "total_kills": 850,
    "total_deaths": 320,
    "total_assists": 780,
    "favorite_champion": "Azir",
    "longest_game_minutes": 45.2
  },
  
  "creative_summary": "What an incredible year for Faker...",
  "motivational_message": "Keep pushing, your growth is remarkable..."
}
```

---

### Generate Social Card
Generate a shareable social media card image.

**Endpoint:** `POST /api/visualizations/social-card`

**Request Body:**
Send the full insights object from `/insights` endpoint.

**Response:**
- Content-Type: `image/jpeg`
- Binary image data (1200x630 pixels)

**Usage:**
```javascript
fetch('/api/visualizations/social-card', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(insightsData)
})
.then(res => res.blob())
.then(blob => {
  const url = URL.createObjectURL(blob);
  // Download or display image
});
```

---

## Rate Limiting

The API implements rate limiting to comply with Riot API restrictions:

- **20 requests per second**
- **100 requests per 2 minutes**

Requests are automatically throttled and queued. If limits are exceeded, you'll receive:

```json
{
  "error": "Rate limit exceeded"
}
```

Wait a few seconds and retry.

---

## Caching

Responses are cached for 24 hours (configurable) to improve performance and reduce API calls.

Cache keys are based on:
- Player PUUID
- Request parameters (match count, date range)

To bypass cache, wait for cache expiry or restart the service.

---

## Error Handling

All errors follow this format:

```json
{
  "error": "Error message describing what went wrong"
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - Player or data not found |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |

---

## Examples

### Complete Flow Example

```javascript
// 1. Lookup player
const lookupResponse = await fetch('/api/player/lookup', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    game_name: 'Faker',
    tag_line: 'KR1'
  })
});
const { puuid } = await lookupResponse.json();

// 2. Generate insights
const insightsResponse = await fetch(`/api/player/${puuid}/insights`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    player_name: 'Faker',
    max_matches: 50
  })
});
const insights = await insightsResponse.json();

// 3. Generate social card
const cardResponse = await fetch('/api/visualizations/social-card', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(insights)
});
const imageBlob = await cardResponse.blob();
```

### cURL Examples

**Lookup Player:**
```bash
curl -X POST http://localhost:5000/api/player/lookup \
  -H "Content-Type: application/json" \
  -d '{"game_name":"Faker","tag_line":"KR1"}'
```

**Generate Insights:**
```bash
curl -X POST http://localhost:5000/api/player/ABC123/insights \
  -H "Content-Type: application/json" \
  -d '{"player_name":"Faker","max_matches":50}'
```

**Download Social Card:**
```bash
curl -X POST http://localhost:5000/api/visualizations/social-card \
  -H "Content-Type: application/json" \
  -d @insights.json \
  --output social-card.jpg
```

---

## Best Practices

1. **Cache PUUIDs**: Store player PUUIDs to avoid repeated lookups
2. **Handle Errors**: Always check response status codes
3. **Rate Limiting**: Implement client-side throttling
4. **Progressive Loading**: Fetch data in stages for better UX
5. **Validate Input**: Sanitize user input before sending

---

## Support

For API support:
- Check [SETUP.md](SETUP.md) for configuration
- Review [README.md](README.md) for features
- Open an issue on GitHub
