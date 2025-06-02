"""
Security Blueprint Package.

This package handles all authentication, authorization, and user management functionality
for the application, including:

- User registration and login
- Password reset flows
- Token management for API authentication
- Account approval workflows
- Authentication and authorization decorators

All routes in this blueprint are prefixed with '/api/security'.
"""
from flask import Blueprint

# Create the security blueprint
security = Blueprint('security', __name__)

# Import package components to register them with the blueprint
# Imports are at the bottom to avoid circular import issues
from . import routes, models, forms, serializers