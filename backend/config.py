import os
from datetime import timedelta

class Config:
    """Configuration class for EduCore application"""
    
    # Flask Configuration
    DEBUG = True
    TESTING = False
    HOST = '0.0.0.0'
    PORT = 5000
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    
    # Database Configuration
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'educore')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # JWT Configuration (for API tokens)
    JWT_SECRET = os.environ.get('JWT_SECRET', 'jwt-secret-key')
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION = 3600  # 1 hour
    
    # File Upload Configuration
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'gif', 'doc', 'docx', 'xls', 'xlsx'}
    
    # Application Settings
    APP_NAME = 'EduCore'
    APP_VERSION = '1.0.0'
    APP_TIMEZONE = 'Asia/Karachi'
    
    # Email Configuration (Optional)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@educore.com')
    
    # Pagination
    ITEMS_PER_PAGE = 20
    
    # Logging
    LOG_FILE = 'logs/educore.log'
    LOG_LEVEL = 'INFO'
    
    # Security
    PASSWORD_MIN_LENGTH = 8
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_TIME = 15  # minutes

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    DB_NAME = 'educore_test'
