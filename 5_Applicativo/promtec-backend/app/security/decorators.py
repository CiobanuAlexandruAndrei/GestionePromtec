"""
Security decorators module.

This module provides authentication and authorization decorators for protecting API endpoints.
It includes decorators for both basic authentication and admin-only access control.
"""
from functools import wraps
from flask import jsonify, request, current_app

def auth_required(f):
    """
    Authentication decorator that ensures a valid user token is provided.
    
    This decorator checks for a valid Bearer token in the Authorization header of the request.
    The token is verified against the Token database model and ensures the associated user exists.
    
    Args:
        f (function): The Flask route function to be decorated.
        
    Returns:
        function: The decorated function that checks authentication before proceeding.
        
    Response codes:
        - 401: Returned when token is missing, invalid, or the user doesn't exist.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        from .models import User, Token
        
        # Check if Authorization header exists and has correct format
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authentication required'}), 401
            
        # Extract token value
        token = auth_header.split(' ')[1]
        token_obj = Token.query.filter_by(token=token).first()
        
        # Verify token exists in database
        if not token_obj:
            return jsonify({'error': 'Invalid or expired token'}), 401
            
        # Get user associated with token
        current_user = User.query.get(token_obj.user_id)
        
        # Verify user exists
        if not current_user:
            return jsonify({'error': 'User not found'}), 401
            
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    """
    Admin authorization decorator that ensures a valid token is provided and the user has admin privileges.
    
    This decorator extends the authentication check with an additional admin role verification.
    It first performs the same Bearer token validation as auth_required, then checks if the user
    has administrative privileges before allowing access to the protected endpoint.
    
    Args:
        f (function): The Flask route function to be decorated.
        
    Returns:
        function: The decorated function that checks admin authorization before proceeding.
        
    Response codes:
        - 401: Returned when token is missing, invalid, or the user doesn't exist.
        - 403: Returned when the user is authenticated but lacks admin privileges.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        from .models import User, Token
        
        # Check if Authorization header exists and has correct format
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authentication required'}), 401
            
        # Extract token value
        token = auth_header.split(' ')[1]
        token_obj = Token.query.filter_by(token=token).first()
        
        # Verify token exists in database
        if not token_obj:
            return jsonify({'error': 'Invalid or expired token'}), 401
            
        # Get user associated with token
        current_user = User.query.get(token_obj.user_id)
        
        # Verify user exists
        if not current_user:
            return jsonify({'error': 'User not found'}), 401
            
        # Verify user has admin privileges
        if not current_user.is_admin:
            return jsonify({'error': 'Admin privileges required'}), 403
            
        return f(*args, **kwargs)
    return decorated