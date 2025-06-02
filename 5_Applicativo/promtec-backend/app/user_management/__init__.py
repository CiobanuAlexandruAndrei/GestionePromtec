"""
User Management Blueprint Package.

This package handles administrative user management functionality for the application,
including listing, approving, rejecting, and managing user accounts. It works in
conjunction with the security module but focuses specifically on administrative
operations performed on user accounts rather than authentication flows.

All routes in this blueprint are prefixed with '/api/user-management' and most
require administrative privileges.
"""
from flask import Blueprint

# Create the user_management blueprint
user_management = Blueprint('user_management', __name__)

# Import routes to register them with the blueprint
# Import is at the bottom to avoid circular import issues
from . import routes