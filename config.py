import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

class Config:
    """Base configuration class."""
    
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-furkan123'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # AI Configuration
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    # File handling
    TEMP_DIR = 'temp'
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {
        'python': ['.py'],
        'javascript': ['.js', '.mjs']
    }
    
    # analiz ayarları
    STATIC_ANALYSIS_TIMEOUT = 30  # saniye
    AI_ANALYSIS_TIMEOUT = 60  # saniye
    MAX_ISSUES_PER_CATEGORY = 5  # her kategori için maksimum sorun sayısı
    
    # Cleanup settings
    TEMP_FILE_MAX_AGE_HOURS = 24
    CLEANUP_INTERVAL_HOURS = 6

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    SECRET_KEY = 'test-secret-key'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """environment'e göre uygun yapılandırmayı döner."""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])