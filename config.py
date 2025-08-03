import os
import secrets

class Config:
    # Security Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_urlsafe(32)
    
    # Database Configuration  
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///users.db'
    
    # Environment Configuration
    FLASK_ENV = os.environ.get('FLASK_ENV') or 'development'
    
    # Rate Limiting Configuration
    RATE_LIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'memory://'
    
    # Security Headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY', 
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'"
    }
    
    # CORS Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'localhost:3000,localhost:8080').split(',')
    
    # File Upload Security
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False 
    TESTING = False
    
    # Production-specific overrides
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_urlsafe(32)
    
    # Only require SECRET_KEY if actually deploying to production
    if os.environ.get('FLASK_ENV') == 'production' and not os.environ.get('SECRET_KEY'):
        raise ValueError("SECRET_KEY environment variable must be set in production")

class TestingConfig(Config):
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'  # In-memory database for tests

def get_config():
    """Get configuration based on environment."""
    env = os.environ.get('FLASK_ENV', 'development')
    
    if env == 'production':
        return ProductionConfig()
    elif env == 'testing':
        return TestingConfig()
    else:
        return DevelopmentConfig()
