"""
Schools Blueprint Package.

This package manages the schools functionality of the application, providing
API endpoints for creating, listing, updating, and deleting schools in the system.
Schools are referenced by student enrollments and user accounts.

All routes in this blueprint are prefixed with '/api/schools', and modification
operations require administrator privileges.
"""
from flask import Blueprint

# Create the schools blueprint
schools = Blueprint('schools', __name__)

# Import routes to register them with the blueprint
# Import is at the bottom to avoid circular import issues
from . import routes