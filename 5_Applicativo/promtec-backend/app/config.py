"""
Application Configuration Module.

This module contains the configuration settings for the Flask application,
including database connection parameters, security settings, and CORS configuration.
It loads settings from environment variables for better security and deployment flexibility.
"""
import os
from dotenv import load_dotenv  # For loading environment variables from .env file
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Base directory of the application (one level up from this file)
BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    """
    Configuration class containing all settings for the Flask application.
    
    This class defines configuration variables that Flask and its extensions will use.
    Most sensitive values are loaded from environment variables for security.
    """
    # Flask debug mode (should be False in production)
    DEBUG = True

    # CSRF protection setting (should be True in production)
    WTF_CSRF_ENABLED = False

    # Database connection settings from environment variables
    DB_USER = os.environ.get('DB_USER')  # Database username
    DB_PASSWORD = os.environ.get('DB_PASSWORD')  # Database password
    DB_HOST = os.environ.get('DB_HOST', 'mysql')  # Database host, defaults to 'mysql' for Docker
    DB_PORT = os.environ.get('DB_PORT')  # Database port
    DB_NAME = os.environ.get('DB_NAME')  # Database name

    # SQLAlchemy database connection string using PyMySQL driver
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    # Disable SQLAlchemy event system (not needed and improves performance)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CORS settings to control cross-origin resource sharing
    CORS_ALLOWED_ORIGINS = ['*']  # Allow all origins (should be restricted in production)
    # Headers that are allowed in cross-origin requests
    CORS_ALLOW_HEADERS = [
        'accept',
        'accept-encoding',
        'authorization',  # For authentication tokens
        'content-type',
        'dnt',  # Do Not Track
        'origin',
        'user-agent',
        'x-csrftoken',  # For CSRF protection
        'x-requested-with',
    ]



