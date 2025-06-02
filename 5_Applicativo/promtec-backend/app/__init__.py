"""
Promtec Backend Application Package.

This package contains the main Flask application factory and all its components.
It initializes the application, registers blueprints, sets up database connections,
configures CORS, and starts background jobs for scheduled tasks.
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from dotenv import load_dotenv  # For loading environment variables from .env file
from flask import Flask, request
from .config import Config  # Application configuration
from .extensions import db, migrate, cors, ma  # Flask extensions
from flask_wtf.csrf import CSRFProtect  # CSRF protection
from .security.routes import create_default_user  # Default admin user creation
from .schools.defaults import create_default_schools  # Default schools setup
from apscheduler.schedulers.background import BackgroundScheduler  # Scheduler for background tasks
from .slots.models import EnrollmentActivity  # Model for enrollment activities
import atexit  # For registering shutdown handlers


def create_app():
    """
    Flask application factory function.
    
    This function creates and configures the Flask application instance, including:
    - Loading environment variables from .env file
    - Setting up configuration from Config class
    - Initializing database and extensions
    - Registering blueprints for API routes
    - Creating database tables and default data if needed
    - Setting up background tasks for periodic operations
    
    Returns:
        Flask: The configured Flask application instance ready to be run
    """
    # Load environment variables from .env file
    load_dotenv()

    # Create Flask application instance
    app = Flask(__name__)
    app.config.from_object(Config)  # Apply configuration from Config class
    app.secret_key = os.environ.get('FLASK_SECRET_KEY')  # Set secret key for sessions and CSRF
    
    # Set up error logging
    log_dir = Path(os.environ.get('LOG_DIR', 'logs'))
    # Create logs directory if it doesn't exist
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure logging for application errors
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    error_log_file = log_dir / 'errors.log'
    
    # Create a file handler for error logs with rotation (max 10MB, keep 10 backup files)
    file_handler = RotatingFileHandler(error_log_file, maxBytes=10485760, backupCount=10)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.ERROR)
    
    # Add the logger to the application
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.ERROR)
    
    # Set up request logging for failed requests
    @app.after_request
    def log_response(response):
        if response.status_code >= 400:
            app.logger.error(
                'Request: %s %s -> %s',
                request.method,
                request.path,
                response.status_code
            )
        return response
            
    # Register error handler for 500 errors
    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.error('Server Error: %s', error)
        app.logger.error('Request: %s %s', request.method, request.path)
        return {'error': 'Internal server error'}, 500

    # Initialize Flask extensions
    db.init_app(app)  # SQLAlchemy database
    migrate.init_app(app, db)  # Alembic migrations
    cors.init_app(app, resources={r"/*": {"origins": "*"}})  # Cross-Origin Resource Sharing
    ma.init_app(app)  # Marshmallow serialization
    csrf = CSRFProtect()
    csrf.init_app(app)  # CSRF protection

    # Configure application components with application context
    with app.app_context():
        # Import blueprints (must be inside context to avoid circular imports)
        from .security import security as security_blueprint
        from .user_management import user_management as user_management_blueprint
        from .schools import schools as schools_blueprint
        from .slots import slots as slots_blueprint
        from .schools.models import School

        # Register blueprints with URL prefixes
        app.register_blueprint(security_blueprint, url_prefix='/api/security')
        app.register_blueprint(user_management_blueprint, url_prefix='/api/user-management')
        app.register_blueprint(schools_blueprint, url_prefix='/api/schools')
        app.register_blueprint(slots_blueprint, url_prefix='/api/slots')

        # Create database tables and initial data
        db.create_all()
        create_default_user()  # Create default admin user if none exists
        create_default_schools(db, School)  # Create default schools if none exist

        # Create background scheduler for periodic tasks
        scheduler = BackgroundScheduler()
        scheduler.add_job(func=lambda: check_enrollment_summaries(app), trigger="interval", minutes=1)
        scheduler.start()

        # Register scheduler shutdown handler to run when application exits
        atexit.register(lambda: scheduler.shutdown())

    return app


def check_enrollment_summaries(app):
    """
    Check for pending enrollment summaries that need to be sent to users.
    
    This function is called periodically by the background scheduler to process
    any enrollment activities that require email notifications to be sent. It ensures
    that the function runs within the application context, so all database operations
    and Flask extensions are available.
    
    Args:
        app (Flask): The Flask application instance to create context from
    """
    with app.app_context():
        EnrollmentActivity.check_and_send_summaries()