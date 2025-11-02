"""
AWS AI Services Integration
Provides Amazon Bedrock for natural language generation and SageMaker for ML predictions
"""
import json
import logging
from typing import Dict, List, Optional, Any
import boto3
from botocore.exceptions import ClientError, BotoCoreError
from config.settings import config

logger = logging.getLogger(__name__)


class AWSServicesError(Exception):
    """Custom exception for AWS service errors"""
    pass


class BedrockService:
    """Amazon Bedrock service for AI-generated content"""
    
    def __init__(self):
        """Initialize Bedrock client"""
        try:
            self.client = boto3.client(
                'bedrock-runtime',
                region_name=config.AWS_REGION,
                aws_access_key_id=config.AWS_ACCESS_KEY_ID if config.AWS_ACCESS_KEY_ID else None,
                aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY if config.AWS_SECRET_ACCESS_KEY else None,
            )
            self.model_id = config.BEDROCK_MODEL_ID
            self.enabled = config.ENABLE_BEDROCK
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            self.client = None
            self.enabled = False
    
    def generate_text(self, prompt: str, max_tokens: Optional[int] = None,
                     temperature: Optional[float] = None, system_prompt: Optional[str] = None) -> str:
        """
        Generate text using Amazon Bedrock
        
        Args:
            prompt: User prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            system_prompt: System prompt for context
            
        Returns:
            Generated text
        """
        if not self.enabled or not self.client:
            logger.warning("Bedrock is not enabled or client not initialized")
            return self._generate_fallback_text(prompt)
        
        max_tokens = max_tokens or config.BEDROCK_MAX_TOKENS
        temperature = temperature if temperature is not None else config.BEDROCK_TEMPERATURE
        
        try:
            # Prepare request based on model
            if 'claude' in self.model_id.lower():
                body = self._prepare_claude_request(prompt, max_tokens, temperature, system_prompt)
            elif 'titan' in self.model_id.lower():
                body = self._prepare_titan_request(prompt, max_tokens, temperature)
            else:
                raise AWSServicesError(f"Unsupported model: {self.model_id}")
            
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            
            # Extract text based on model
            if 'claude' in self.model_id.lower():
                return self._extract_claude_response(response_body)
            elif 'titan' in self.model_id.lower():
                return self._extract_titan_response(response_body)
            
        except (ClientError, BotoCoreError) as e:
            logger.error(f"Bedrock API error: {e}")
            return self._generate_fallback_text(prompt)
        except Exception as e:
            logger.error(f"Unexpected error in Bedrock generation: {e}")
            return self._generate_fallback_text(prompt)
    
    def generate_player_summary(self, player_data: Dict, stats: Dict) -> str:
        """
        Generate personalized year-end summary for a player
        
        Args:
            player_data: Player information
            stats: Overall statistics
            
        Returns:
            Creative summary text
        """
        prompt = f"""Create an engaging, personalized year-end gaming summary for a League of Legends player.

Player Stats:
- Total Games: {stats.get('total_games', 0)}
- Win Rate: {stats.get('win_rate', 0)}%
- Average KDA: {stats.get('avg_kda', 0)}
- Total Pentas: {stats.get('total_penta_kills', 0)}
- Total Hours Played: {stats.get('total_time_played_hours', 0)}

Write a fun, motivational summary (200-300 words) that:
1. Celebrates their achievements
2. Highlights memorable moments
3. Includes light humor
4. Ends with encouragement for next year

Make it personal, engaging, and shareable on social media."""

        system_prompt = "You are a friendly League of Legends coach creating personalized year-end summaries for players. Be enthusiastic, supportive, and entertaining."
        
        return self.generate_text(prompt, max_tokens=500, system_prompt=system_prompt)
    
    def generate_coaching_tips(self, weaknesses: Dict, champion_stats: List[Dict], 
                              recent_performance: Dict) -> List[str]:
        """
        Generate personalized coaching tips
        
        Args:
            weaknesses: Identified weaknesses
            champion_stats: Champion performance data
            recent_performance: Recent game trends
            
        Returns:
            List of actionable coaching tips
        """
        weakness_text = "\n".join([
            f"- {k}: {v.get('metric')} = {v.get('value')} ({v.get('severity')} priority)"
            for k, v in weaknesses.items()
        ])
        
        prompt = f"""Generate 5 specific, actionable coaching tips for a League of Legends player based on their performance data.

Identified Weaknesses:
{weakness_text if weakness_text else "No major weaknesses identified"}

Recent Performance:
- Recent Win Rate: {recent_performance.get('win_rate', 'N/A')}%
- Recent Avg KDA: {recent_performance.get('avg_kda', 'N/A')}

Provide 5 concrete tips that:
1. Address specific weaknesses
2. Are immediately actionable
3. Include clear steps to implement
4. Are personalized to their playstyle

Format: Return only a numbered list (1-5) with each tip on a new line."""

        system_prompt = "You are an expert League of Legends coach providing practical, actionable advice."
        
        response = self.generate_text(prompt, max_tokens=800, system_prompt=system_prompt)
        
        # Parse response into list
        tips = [line.strip() for line in response.split('\n') if line.strip() and line.strip()[0].isdigit()]
        return tips[:5] if tips else self._generate_fallback_tips(weaknesses)
    
    def generate_motivational_message(self, player_name: str, best_champion: str, 
                                     win_rate: float, improvement_area: str) -> str:
        """
        Generate a motivational message
        
        Args:
            player_name: Player's name
            best_champion: Best performing champion
            win_rate: Overall win rate
            improvement_area: Key area to improve
            
        Returns:
            Motivational message
        """
        prompt = f"""Write a short, motivational message (50-75 words) for a League of Legends player.

Player: {player_name}
Best Champion: {best_champion}
Win Rate: {win_rate}%
Focus Area: {improvement_area}

Make it encouraging, specific to their situation, and inspiring for continued improvement."""

        system_prompt = "You are a supportive gaming coach providing motivation."
        
        return self.generate_text(prompt, max_tokens=150, system_prompt=system_prompt)
    
    @staticmethod
    def _prepare_claude_request(prompt: str, max_tokens: int, temperature: float,
                                system_prompt: Optional[str] = None) -> Dict:
        """Prepare request body for Claude models"""
        messages = [{"role": "user", "content": prompt}]
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }
        
        if system_prompt:
            body["system"] = system_prompt
        
        return body
    
    @staticmethod
    def _prepare_titan_request(prompt: str, max_tokens: int, temperature: float) -> Dict:
        """Prepare request body for Titan models"""
        return {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": max_tokens,
                "temperature": temperature,
                "topP": 0.9
            }
        }
    
    @staticmethod
    def _extract_claude_response(response_body: Dict) -> str:
        """Extract text from Claude response"""
        content = response_body.get('content', [])
        if content and len(content) > 0:
            return content[0].get('text', '')
        return ''
    
    @staticmethod
    def _extract_titan_response(response_body: Dict) -> str:
        """Extract text from Titan response"""
        results = response_body.get('results', [])
        if results and len(results) > 0:
            return results[0].get('outputText', '')
        return ''
    
    @staticmethod
    def _generate_fallback_text(prompt: str) -> str:
        """Generate simple fallback text when Bedrock is unavailable"""
        return "AI-generated content is currently unavailable. Please check your AWS configuration."
    
    @staticmethod
    def _generate_fallback_tips(weaknesses: Dict) -> List[str]:
        """Generate fallback coaching tips"""
        tips = []
        for weakness, data in weaknesses.items():
            tips.append(f"{data.get('suggestion', 'Focus on improvement')}")
        return tips[:5]


class SageMakerService:
    """Amazon SageMaker service for ML predictions"""
    
    def __init__(self):
        """Initialize SageMaker client"""
        try:
            self.client = boto3.client(
                'sagemaker-runtime',
                region_name=config.AWS_REGION,
                aws_access_key_id=config.AWS_ACCESS_KEY_ID if config.AWS_ACCESS_KEY_ID else None,
                aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY if config.AWS_SECRET_ACCESS_KEY else None,
            )
            self.endpoint_name = config.SAGEMAKER_ENDPOINT_NAME
            self.enabled = config.ENABLE_SAGEMAKER and bool(self.endpoint_name)
        except Exception as e:
            logger.error(f"Failed to initialize SageMaker client: {e}")
            self.client = None
            self.enabled = False
    
    def predict_performance(self, features: Dict) -> Dict:
        """
        Predict player performance using SageMaker endpoint
        
        Args:
            features: Feature dictionary for prediction
            
        Returns:
            Prediction results
        """
        if not self.enabled or not self.client:
            logger.warning("SageMaker is not enabled or endpoint not configured")
            return self._fallback_prediction(features)
        
        try:
            response = self.client.invoke_endpoint(
                EndpointName=self.endpoint_name,
                ContentType='application/json',
                Body=json.dumps(features)
            )
            
            result = json.loads(response['Body'].read().decode())
            return result
            
        except (ClientError, BotoCoreError) as e:
            logger.error(f"SageMaker API error: {e}")
            return self._fallback_prediction(features)
        except Exception as e:
            logger.error(f"Unexpected error in SageMaker prediction: {e}")
            return self._fallback_prediction(features)
    
    def predict_improvement_areas(self, player_stats: Dict) -> List[Dict]:
        """
        Predict areas where player is most likely to improve
        
        Args:
            player_stats: Player statistics
            
        Returns:
            List of improvement predictions with confidence scores
        """
        features = {
            'win_rate': player_stats.get('win_rate', 0),
            'avg_kda': player_stats.get('avg_kda', 0),
            'avg_cs_per_minute': player_stats.get('avg_cs_per_minute', 0),
            'avg_vision_score': player_stats.get('avg_vision_score', 0),
            'avg_damage': player_stats.get('avg_damage_dealt', 0),
            'total_games': player_stats.get('total_games', 0),
        }
        
        prediction = self.predict_performance(features)
        
        # Process prediction into improvement areas
        improvement_areas = []
        
        if 'predictions' in prediction:
            for area, confidence in prediction['predictions'].items():
                improvement_areas.append({
                    'area': area,
                    'confidence': confidence,
                    'priority': 'high' if confidence > 0.7 else 'medium' if confidence > 0.4 else 'low'
                })
        
        return sorted(improvement_areas, key=lambda x: x['confidence'], reverse=True)
    
    @staticmethod
    def _fallback_prediction(features: Dict) -> Dict:
        """Provide fallback prediction when SageMaker is unavailable"""
        return {
            'predictions': {
                'mechanics': 0.5,
                'decision_making': 0.5,
                'vision_control': 0.5,
                'champion_mastery': 0.5
            },
            'note': 'Using fallback predictions - SageMaker endpoint not configured'
        }


class S3StorageService:
    """Amazon S3 service for storing visualizations and data"""
    
    def __init__(self):
        """Initialize S3 client"""
        try:
            self.client = boto3.client(
                's3',
                region_name=config.AWS_REGION,
                aws_access_key_id=config.AWS_ACCESS_KEY_ID if config.AWS_ACCESS_KEY_ID else None,
                aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY if config.AWS_SECRET_ACCESS_KEY else None,
            )
            self.bucket_name = config.S3_BUCKET_NAME
            self.enabled = config.ENABLE_S3_STORAGE
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            self.client = None
            self.enabled = False
    
    def upload_file(self, file_path: str, s3_key: str, content_type: Optional[str] = None) -> Optional[str]:
        """
        Upload file to S3
        
        Args:
            file_path: Local file path
            s3_key: S3 object key
            content_type: MIME type
            
        Returns:
            Public URL or None if failed
        """
        if not self.enabled or not self.client:
            logger.warning("S3 storage is not enabled")
            return None
        
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            self.client.upload_file(file_path, self.bucket_name, s3_key, ExtraArgs=extra_args)
            
            url = f"https://{self.bucket_name}.s3.{config.AWS_REGION}.amazonaws.com/{s3_key}"
            return url
            
        except (ClientError, BotoCoreError) as e:
            logger.error(f"S3 upload error: {e}")
            return None
    
    def upload_bytes(self, data: bytes, s3_key: str, content_type: Optional[str] = None) -> Optional[str]:
        """
        Upload bytes to S3
        
        Args:
            data: Bytes to upload
            s3_key: S3 object key
            content_type: MIME type
            
        Returns:
            Public URL or None if failed
        """
        if not self.enabled or not self.client:
            logger.warning("S3 storage is not enabled")
            return None
        
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=data,
                **extra_args
            )
            
            url = f"https://{self.bucket_name}.s3.{config.AWS_REGION}.amazonaws.com/{s3_key}"
            return url
            
        except (ClientError, BotoCoreError) as e:
            logger.error(f"S3 upload error: {e}")
            return None
    
    def generate_presigned_url(self, s3_key: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate presigned URL for S3 object
        
        Args:
            s3_key: S3 object key
            expiration: URL expiration in seconds
            
        Returns:
            Presigned URL or None if failed
        """
        if not self.enabled or not self.client:
            return None
        
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return url
        except (ClientError, BotoCoreError) as e:
            logger.error(f"Error generating presigned URL: {e}")
            return None


# Singleton instances
bedrock_service = BedrockService()
sagemaker_service = SageMakerService()
s3_service = S3StorageService()
