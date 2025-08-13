import os
from dotenv import load_dotenv

load_dotenv()

# We'll use a constant for the database file name to keep it consistent
DATABASE_FILE = "compression_db.sqlite"

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # SQLite uses a file-based database, so we'll remove the MySQL-specific variables
    
    # Database configuration for SQLite
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_FILE}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    COMPRESSED_FOLDER = os.path.join(os.getcwd(), 'compressed')
    
    # Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Compression settings
    COMPRESSION_TIMEOUT = 300  # 5 minutes timeout for compression
    MAX_DICTIONARY_SIZE = 4096  # Maximum LZW dictionary size

class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}