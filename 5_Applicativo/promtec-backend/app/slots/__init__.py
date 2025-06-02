"""
Slots Blueprint Package.

This package manages the enrollment slot functionality of the application,
including creating, reading, updating, and deleting slots, as well as
managing student enrollments and waiting lists.

All routes in this blueprint require authentication and are prefixed with '/api/slots'.
"""
from flask import Blueprint

# Create the slots blueprint
slots = Blueprint('slots', __name__)

# Import routes to register them with the blueprint
# Import is at the bottom to avoid circular import issues
from . import routes