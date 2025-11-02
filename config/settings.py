"""
Configuration settings for LoL Analytics Agent
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Riot API
    RIOT_API_KEY = os.getenv('RIOT_API_KEY', '')
    RIOT_API_REGION = os.getenv('RIOT_API_REGION', 'americas')
    RIOT_API_PLATFORM = os.getenv('RIOT_API_PLATFORM', 'na1')
    RIOT_RATE_LIMIT_PER_SECOND = int(os.getenv('RIOT_RATE_LIMIT_PER_SECOND', '20'))
    RIOT_RATE_LIMIT_PER_MINUTE = int(os.getenv('RIOT_RATE_LIMIT_PER_MINUTE', '100'))
    
    # AWS Configuration
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
    
    # AWS Bedrock
    BEDROCK_MODEL_ID = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
    BEDROCK_TEMPERATURE = float(os.getenv('BEDROCK_TEMPERATURE', '0.7'))
    BEDROCK_MAX_TOKENS = int(os.getenv('BEDROCK_MAX_TOKENS', '2000'))
    
    # AWS SageMaker
    SAGEMAKER_ENDPOINT_NAME = os.getenv('SAGEMAKER_ENDPOINT_NAME', '')
    
    # AWS S3
    S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'lol-analytics-data')
    S3_VISUALIZATIONS_PREFIX = 'visualizations/'
    S3_PROCESSED_DATA_PREFIX = 'processed-data/'
    
    # Redis Cache
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
    REDIS_DB = int(os.getenv('REDIS_DB', '0'))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
    CACHE_EXPIRY_HOURS = int(os.getenv('CACHE_EXPIRY_HOURS', '24'))
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///lol_analytics.db')
    
    # Analytics Settings
    MATCH_HISTORY_LIMIT = int(os.getenv('MATCH_HISTORY_LIMIT', '100'))
    MIN_MATCHES_FOR_INSIGHTS = int(os.getenv('MIN_MATCHES_FOR_INSIGHTS', '10'))
    ANALYSIS_LOOKBACK_DAYS = int(os.getenv('ANALYSIS_LOOKBACK_DAYS', '365'))
    
    # Feature Flags
    ENABLE_SAGEMAKER = os.getenv('ENABLE_SAGEMAKER', 'False').lower() == 'true'
    ENABLE_BEDROCK = os.getenv('ENABLE_BEDROCK', 'True').lower() == 'true'
    ENABLE_S3_STORAGE = os.getenv('ENABLE_S3_STORAGE', 'False').lower() == 'true'
    ENABLE_REDIS_CACHE = os.getenv('ENABLE_REDIS_CACHE', 'False').lower() == 'true'


config = Config()
