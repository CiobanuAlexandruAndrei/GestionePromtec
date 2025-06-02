"""
Flask Extensions Module.

This module initializes all the Flask extensions used in the application.
The extensions are created here without initializing them with the Flask app.
They will be initialized in the create_app() factory function.
"""
from flask_sqlalchemy import SQLAlchemy  # ORM for database operations
from flask_migrate import Migrate  # Database migration tool built on Alembic
from flask_cors import CORS  # Cross-Origin Resource Sharing support
from flask_marshmallow import Marshmallow  # Object serialization/deserialization library

# SQLAlchemy instance for ORM database operations
db = SQLAlchemy()

# Migrate instance for managing database migrations
migrate = Migrate()

# CORS instance for handling Cross-Origin Resource Sharing
cors = CORS()

# Marshmallow instance for object serialization/deserialization
ma = Marshmallow()
