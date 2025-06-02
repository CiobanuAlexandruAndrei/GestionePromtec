from flask import request, jsonify, url_for, current_app
from flask_httpauth import HTTPTokenAuth
from werkzeug.security import check_password_hash, generate_password_hash
from ..extensions import db
from .models import User, Token, School, PasswordResetToken, UserApproval
import secrets
from . import security
from .forms import RegistrationForm, LoginForm
import os
from dotenv import load_dotenv
from ..utils.email_utils import send_password_reset_email, send_account_approval_email
from .decorators import admin_required, auth_required

auth = HTTPTokenAuth(scheme='Bearer')
load_dotenv()

@security.route('/create_user', methods=['POST'])
def create_user():
    """
    Register a new user in the system.
    
    This endpoint processes user registration forms, creating new user accounts or
    reactivating soft-deleted accounts. It validates the registration form data,
    hashes passwords securely, and sets up the user for the approval process.
    
    Request Body (form data):
        email: User's email address (unique identifier)
        password: User's chosen password (will be hashed)
        first_name: User's first name
        last_name: User's last name
        school_name: Name of the school the user is associated with
        
    Returns:
        201: JSON response with success message when user is created or restored
        400: JSON response with form validation errors
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if a soft-deleted user with this email already exists
        existing_user = User.query.filter_by(email=form.email.data, deleted=True).first()
        
        if existing_user:
            existing_user.deleted = False
            existing_user.password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
            existing_user.first_name = form.first_name.data
            existing_user.last_name = form.last_name.data
            existing_user.school_name = form.school_name.data
            existing_user.is_active = True
            existing_user.is_approved = False  # Reset approval status
            
            # Remove any existing approval records for this user
            UserApproval.query.filter_by(user_to_approve_id=existing_user.id).delete()
            
            db.session.commit()
            
            return jsonify({
                'message': 'User account restored successfully',
            }), 201
        else:
            # Create a new user if no soft-deleted account exists
            hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
            
            new_user = User(
                password=hashed_password,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                school_name=form.school_name.data,
                is_active=True
            )
            db.session.add(new_user)
            db.session.commit()
            
            return jsonify({
                'message': 'User created successfully',
            }), 201
    
    return jsonify({'errors': form.errors}), 400

@security.route('/login', methods=['POST'])
def login_view():
    """
    Authenticate a user and issue an access token.
    
    This endpoint processes login attempts, validating credentials and checking account
    status (active, approved, rejected). It returns appropriate error messages for
    various account states and generates a new authentication token upon successful login.
    
    Request Body (form data):
        username: User's email address
        password: User's password
        
    Returns:
        200: JSON response with token and user information on successful login
        400: JSON response with form validation errors or invalid credentials
        403: JSON response with appropriate error message for inactive/unapproved accounts
    """
    form = LoginForm()
    if form.validate_on_submit():
        # Find user by email
        user = User.query.filter_by(email=form.username.data, deleted=False).first()
        
        # First check if user exists and handle account status checks
        if user:
            # Check for deactivated accounts
            if not user.is_active:
                return jsonify({
                    'error': 'Il tuo account è attualmente disattivato. Contatta un amministratore.'
                }), 403
            
            # For non-admin users, check rejection/approval status
            if not user.is_admin:
                # Get the latest approval record to check if rejected or pending
                latest_approval = UserApproval.query.filter_by(
                    user_to_approve_id=user.id
                ).order_by(UserApproval.created_at.desc()).first()
                
                # If there's an approval record and it's explicitly rejected
                if latest_approval and latest_approval.is_approved == False:
                    return jsonify({
                        'error': 'Il tuo account è stato rifiutato. Contatta l\'amministratore per maggiori informazioni.'
                    }), 403
                # If no approval yet or no record yet
                elif not user.approval_status:
                    return jsonify({
                        'error': 'Il tuo account è in attesa di approvazione. Sarai notificato via email quando un amministratore approverà il tuo account.'
                    }), 403
            
            # Now verify password
            if check_password_hash(user.password, form.password.data):
                # Account is active and approved, generate token
                token = secrets.token_hex(16)
                new_token = Token(user_id=user.id, token=token)
                db.session.add(new_token)
                db.session.commit()
                
                # Return success response with token and user info
                return jsonify({
                    'token': token, 
                    'user': {
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'is_admin': user.is_admin
                    }
                })
            else:
                # Invalid password
                return jsonify({'error': 'Credenziali non valide'}), 400
        
        return jsonify({'error': 'Credenziali non valide'}), 400
    
    return jsonify({'errors': form.errors}), 400

@security.route('/logout', methods=['POST'])
@auth.login_required
def logout_view():
    """
    Invalidate all authentication tokens for the current user.
    
    This endpoint handles user logout by finding and deleting all active tokens
    associated with the authenticated user. It requires a valid authentication token
    to access.
    
    Returns:
        200: JSON response with success message
        401: JSON response with error message if authentication fails
    """
    user = auth.current_user()
    if user:
        tokens = Token.query.filter_by(user_id=user.id).all()
        for token in tokens:
            db.session.delete(token)
        db.session.commit()
        return jsonify({'message': 'Logged out successfully'})
    else:
        return jsonify({'error': 'Unauthorized'}), 401

@security.route('/email/<int:pk>', methods=['GET'])
@auth.login_required
def get_email_view(pk):
    """
    Retrieve the email address of the currently authenticated user.
    
    This endpoint returns the email address of the currently authenticated user.
    It requires a valid authentication token to access.
    
    Args:
        pk (int): Primary key identifier (not used in the current implementation)
        
    Returns:
        200: JSON response with the user's email address
        401: JSON response with error message if authentication fails
    """
    user = auth.current_user()
    if user:
        return jsonify({'user': user.email})
    else:
        return jsonify({'error': 'Unauthorized'}), 401

@security.route('/schools', methods=['GET'])
def get_schools():
    """
    Retrieve a list of all schools in the system.
    
    This endpoint returns a list of all school names registered in the system.
    It is used to populate dropdown menus in the registration form and other
    parts of the application where school selection is required.
    
    Returns:
        200: JSON response with a list of school names
    """
    schools = School.query.all()
    return jsonify({
        'schools': [school.name for school in schools]
    })

@auth.verify_token
def verify_token(token):
    """
    Verify an authentication token and return the associated user.
    
    This function is used by the HTTPTokenAuth extension to validate tokens
    provided in the Authorization header of requests. It looks up the token
    in the database and returns the associated user if the token is valid.
    
    Args:
        token (str): Authentication token to verify
        
    Returns:
        User: User object if the token is valid
        None: If the token is invalid or not found
    """
    #print(f"Verifying token: {token}")  # Debug statement
    token_obj = Token.query.filter_by(token=token).first()
    if token_obj:
        #print(f"Token valid for user_id: {token_obj.user_id}")  # Debug statement
        return User.query.get(token_obj.user_id)
    #print("Token invalid")  # Debug statement
    return None

@security.route('/health', methods=['GET'])
def health_check():
    """
    Simple health check endpoint to verify the backend service is running.
    
    This endpoint is used by monitoring systems or the frontend to verify that
    the backend service is operational. It does not require authentication.
    
    Returns:
        200: JSON response with status information
    """
    return jsonify({
        'status': 'ok',
        'message': 'Backend service is running'
    })

@security.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    Initiate the password reset process for a user.
    
    This endpoint handles the first step in the password reset flow. It validates
    the email address, checks account status (deleted, inactive), and generates
    a secure reset token. An email with the reset link is sent to the user if
    the account exists and is active.
    
    For security reasons, the endpoint always returns a success message even if
    the email doesn't match an account, to prevent email enumeration attacks.
    
    Request Body (JSON):
        email (str): The email address of the account to reset
        
    Returns:
        200: JSON response with a success message (regardless of whether email exists)
        400: JSON response with error if email is missing
        403: JSON response with error for deleted or inactive accounts
    """
    data = request.json
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    # Check if this is a deleted account
    deleted_user = User.query.filter_by(email=email, deleted=True).first()
    if deleted_user:
        return jsonify({'error': 'Il tuo account è stato cancellato, registrati di nuovo'}), 403
        
    # Find user by email
    user = User.query.filter_by(email=email, deleted=False).first()
    
    # We always return success even if user is not found (for security reasons)
    if not user:
        return jsonify({'message': 'Se l\'indirizzo email è valido, riceverai un link per il ripristino della password.'}), 200
    
    # Check if user account is deactivated
    if not user.is_active:
        return jsonify({'error': 'Il tuo account è disattivato, contattare l\'amministratore'}), 403
    
    # Invalidate existing unused tokens for this user
    existing_tokens = PasswordResetToken.query.filter_by(
        user_id=user.id, 
        used=False
    ).all()
    
    for token in existing_tokens:
        token.used = True
        
    db.session.commit()
    
    # Generate new token
    reset_token = PasswordResetToken.generate_token(user.id)
    
    # Construct reset URL
    # In production, this should be a frontend URL, not a backend URL
    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:80')
    reset_url = f"{frontend_url}/reset-password/{reset_token.token}"
    
    # Send email
    user_name = f"{user.first_name} {user.last_name}"
    send_password_reset_email(user.email, user_name, reset_url)
    
    return jsonify({
        'message': 'Se l\'indirizzo email è valido, riceverai un link per il ripristino della password.'
    }), 200

@security.route('/verify-reset-token/<string:token>', methods=['GET'])
def verify_reset_token(token):
    """
    Verify if a password reset token is valid.
    
    This endpoint checks if a given password reset token exists, is unused,
    and has not expired. It's used by the frontend to validate reset tokens
    before showing the password reset form to the user.
    
    Args:
        token (str): The password reset token to verify
        
    Returns:
        200: JSON response with validity status and user email if token is valid
        404: JSON response with error message if token is invalid or expired
    """
    # Check if the token exists and is not used
    token_obj = PasswordResetToken.query.filter_by(token=token, used=False).first()
    
    if not token_obj or not token_obj.is_valid():
        return jsonify({'valid': False, 'error': 'Token non valido o scaduto'}), 400
    
    # Return user information (just email) for confirmation
    user = User.query.get(token_obj.user_id)
    if not user:
        return jsonify({'valid': False, 'error': 'Utente non trovato'}), 400
    
    # Check if user account was deleted
    if user.deleted:
        return jsonify({'valid': False, 'error': 'Il tuo account è stato cancellato, registrati di nuovo'}), 403
    
    # Check if user account is deactivated
    if not user.is_active:
        return jsonify({'valid': False, 'error': 'Il tuo account è disattivato, contattare l\'amministratore'}), 403
    
    return jsonify({
        'valid': True,
        'email': user.email
    }), 200

@security.route('/create-pre-approved-user', methods=['POST'])
@auth.login_required
@admin_required
def create_pre_approved_user():
    """
    Create a new user account that is pre-approved by an administrator.
    
    This endpoint allows administrators to create new user accounts that are
    automatically approved and ready to use. It's typically used to onboard
    new staff members without requiring them to go through the approval process.
    This endpoint requires admin privileges.
    
    Request Body (JSON):
        email (str): User's email address
        first_name (str): User's first name
        last_name (str): User's last name
        school_name (str): Name of the school the user is associated with
        is_admin (bool, optional): Whether the user should have admin privileges
        
    Returns:
        201: JSON response with success message and temporary password
        400: JSON response with validation errors
        401: If authentication fails
        403: If the user isn't an administrator
    """
    data = request.get_json()
    
    # Validate required fields
    if not all(key in data for key in ['first_name', 'last_name', 'email', 'password', 'school_name']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if email already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email già registrata'}), 400
    
    try:
        # Create the user with is_active=True
        hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
        
        new_user = User(
            email=data['email'],
            password=hashed_password,
            first_name=data['first_name'],
            last_name=data['last_name'],
            school_name=data['school_name'],
            is_active=True
        )
        
        # Add and commit the user to get an ID
        db.session.add(new_user)
        db.session.commit()
        
        # Create an approval record for the user
        current_user = auth.current_user()
        approval = UserApproval(
            user_admin_id=current_user.id,
            user_to_approve_id=new_user.id,
            is_approved=True
        )
        
        db.session.add(approval)
        db.session.commit()
        
        # Send the approval email
        send_account_approval_email(new_user.email, f"{new_user.first_name} {new_user.last_name}")
        
        return jsonify({
            'message': 'Utente creato e approvato con successo',
            'user': {
                'id': new_user.id,
                'email': new_user.email,
                'first_name': new_user.first_name,
                'last_name': new_user.last_name
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating pre-approved user: {str(e)}")
        return jsonify({'error': 'Si è verificato un errore nella creazione dell\'utente'}), 500

@security.route('/reset-password/<string:token>', methods=['POST'])
def reset_password(token):
    """
    Reset a user's password using a valid reset token.
    
    This endpoint completes the password reset process by verifying the token
    once more, checking the new password meets requirements, and updating the
    user's password in the database. It also marks the reset token as used to
    prevent reuse.
    
    Args:
        token (str): The password reset token from the URL
        
    Request Body (JSON):
        password (str): The new password for the account
        confirm_password (str): Confirmation of the new password
        
    Returns:
        200: JSON response with success message
        400: JSON response with validation errors
        404: JSON response with error if token is invalid or expired
    """
    data = request.get_json()
    
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    
    if not token or not password:
        return jsonify({'error': 'Token e password sono richiesti'}), 400
    
    # Verify password confirmation
    if password != confirm_password:
        return jsonify({'error': 'Le password non corrispondono'}), 400
    
    # Verify password strength
    if len(password) < 8:
        return jsonify({'error': 'La password deve essere di almeno 8 caratteri'}), 400
    
    # Find the token
    reset_token = PasswordResetToken.query.filter_by(token=token).first()
    
    if not reset_token or not reset_token.is_valid():
        return jsonify({'error': 'Token non valido o scaduto'}), 400
    
    # Get the user
    user = User.query.get(reset_token.user_id)
    if not user:
        return jsonify({'error': 'Utente non trovato'}), 400
    
    # Check if user account was deleted
    if user.deleted:
        return jsonify({'error': 'Il tuo account è stato cancellato, registrati di nuovo'}), 403
    
    # Check if user account is deactivated
    if not user.is_active:
        return jsonify({'error': 'Il tuo account è disattivato, contattare l\'amministratore'}), 403
    
    # Update password
    user.password = generate_password_hash(password, method='pbkdf2:sha256')
    
    # Invalidate token
    reset_token.invalidate()
    
    # Invalidate all existing sessions for security
    for session_token in Token.query.filter_by(user_id=user.id).all():
        db.session.delete(session_token)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Password reimpostata con successo. Ora puoi accedere con la tua nuova password.'
    }), 200

def create_default_user():
    default_email = os.getenv('DEFAULT_ADMIN_EMAIL')
    default_password = os.getenv('DEFAULT_ADMIN_PASSWORD')
    default_first_name = os.getenv('DEFAULT_ADMIN_FIRST_NAME')
    default_last_name = os.getenv('DEFAULT_ADMIN_LAST_NAME')
    
    # Check if default admin already exists
    default_user = User.query.filter_by(email=default_email).first()
    
    if not default_user:
        hashed_password = generate_password_hash(default_password, method='pbkdf2:sha256')
        
        new_user = User(
            email=default_email,
            password=hashed_password,
            first_name=default_first_name,
            last_name=default_last_name,
            is_admin=True,
            is_active=True,
            is_approved=True,
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        print(f"Default admin user created successfully: {default_email}")
    else:
        print(f"Default admin user already exists: {default_email}")


