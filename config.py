"""
Production Configuration for Task Manager API
Environment setup, logging, and production optimizations
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

class ProductionConfig:
    """Production configuration settings"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(32))
    DEBUG = False
    TESTING = False
    
    # Database settings
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'task_manager_prod.db')
    
    # Google API settings
    GOOGLE_CLOUD_PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT_ID')
    CREDENTIALS_PATH = os.environ.get('CREDENTIALS_PATH', 'credentials')
    
    # Logging settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/task_manager.log')
    LOG_MAX_BYTES = int(os.environ.get('LOG_MAX_BYTES', '10485760'))  # 10MB
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', '10'))
    
    # Security settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    API_RATE_LIMIT = os.environ.get('API_RATE_LIMIT', '100/hour')
    
    # Performance settings
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', '1048576'))  # 1MB
    
    @classmethod
    def setup_logging(cls):
        """Setup production logging"""
        # Create logs directory
        os.makedirs(os.path.dirname(cls.LOG_FILE), exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL),
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler with rotation
        file_handler = RotatingFileHandler(
            cls.LOG_FILE,
            maxBytes=cls.LOG_MAX_BYTES,
            backupCount=cls.LOG_BACKUP_COUNT
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        ))
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        ))
        
        # Add handlers to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        # Set specific loggers
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        logging.getLogger('google').setLevel(logging.WARNING)

class DevelopmentConfig:
    """Development configuration settings"""
    
    DEBUG = True
    TESTING = False
    DATABASE_PATH = 'task_manager_dev.db'
    LOG_LEVEL = 'DEBUG'
    
    @classmethod
    def setup_logging(cls):
        """Setup development logging"""
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        )

def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    
    if env == 'production':
        return ProductionConfig
    else:
        return DevelopmentConfig

def setup_app_config(app):
    """Setup Flask app configuration"""
    config = get_config()
    
    # Basic Flask config
    app.config['SECRET_KEY'] = getattr(config, 'SECRET_KEY', os.urandom(32))
    app.config['DEBUG'] = getattr(config, 'DEBUG', False)
    app.config['TESTING'] = getattr(config, 'TESTING', False)
    app.config['MAX_CONTENT_LENGTH'] = getattr(config, 'MAX_CONTENT_LENGTH', 1048576)
    
    # Setup logging
    config.setup_logging()
    
    return config
