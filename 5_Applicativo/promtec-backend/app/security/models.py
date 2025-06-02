"""
Security Models Module.

This module defines the data models for user authentication, authorization,
and security-related operations including user accounts, access tokens,
user approval workflow, and password reset functionality.
"""
from ..extensions import db  # Database ORM instance
from flask_login import UserMixin  # Provides user authentication properties
from datetime import datetime, timedelta  # For token expiration handling
from ..schools.models import School  # For school relationship
import secrets  # For secure token generation

class Token(db.Model):
    """
    Authentication token model for API access.
    
    Stores tokens used for authenticating API requests. Each token is associated
    with a specific user and includes timestamps for creation and updates.
    
    Attributes:
        id (int): Primary key identifier for the token
        user_id (int): Foreign key reference to the user who owns this token
        token (str): The actual token string used for authentication
        created_at (datetime): Timestamp when the token was created
        updated_at (datetime): Timestamp when the token was last updated
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

class User(UserMixin, db.Model):
    """
    User model for authentication and authorization.
    
    This model extends Flask-Login's UserMixin to provide core user authentication
    functionality. It stores user credentials, profile information, administrative
    status, and maintains relationships with other models like schools and tokens.
    
    Attributes:
        id (int): Primary key identifier for the user
        email (str): User's email address (unique, required)
        password (str): Hashed password for authentication
        first_name (str): User's first name
        last_name (str): User's last name
        is_admin (bool): Whether the user has administrative privileges
        is_active (bool): Whether the user account is active
        deleted (bool): Soft delete flag for user accounts
        school_name (str): Foreign key to the school this user belongs to
        school (School): Relationship to the School model
        tokens (list): Relationship to authentication tokens owned by this user
        approvals_received (list): User approval records that this user has received
        approvals_given (list): User approval records that this user has given as an admin
        created_at (datetime): Timestamp when the user account was created
        updated_at (datetime): Timestamp when the user account was last updated
        last_login (datetime): Timestamp of the user's last successful login
        is_approved (bool): Whether the user account has been approved by an admin
    """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)  # Email must be unique
    password = db.Column(db.String(200), nullable=False)  # Stores hashed password

    # User profile information
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))

    # User status flags
    is_admin = db.Column(db.Boolean, default=False, nullable=False)  # Administrative privileges
    is_active = db.Column(db.Boolean, default=True, nullable=False)  # Active account status
    deleted = db.Column(db.Boolean, default=False, nullable=False)  # Soft deletion flag

    # School association
    school_name = db.Column(db.String(50), db.ForeignKey('school.name', name='fk_user_school', ondelete='SET NULL'), nullable=True)
    school = db.relationship('School', backref=db.backref('users', lazy=True))

    # Relationships to other models
    tokens = db.relationship('Token', backref='user', lazy=True)  # Authentication tokens
    approvals_received = db.relationship('UserApproval', backref='user_to_approve', foreign_keys='UserApproval.user_to_approve_id', lazy=True)
    approvals_given = db.relationship('UserApproval', backref='admin_user', foreign_keys='UserApproval.user_admin_id', lazy=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    last_login = db.Column(db.DateTime, nullable=True)

    # Approval status
    is_approved = db.Column(db.Boolean, default=False, nullable=False)  # Latest approval status

    @property
    def approval_status(self):
        """
        Determine and update the user's current approval status.
        
        This property calculates the approval status by:
        1. Automatically approving admin users
        2. For regular users, finding the most recent approval record
        3. Updating the is_approved field if needed to stay in sync
        
        Returns:
            bool: True if the user is approved, False otherwise
        """
        # Admins are automatically approved
        if self.is_admin:
            return True
            
        # Find the most recent approval record for this user
        latest_approval = UserApproval.query.filter_by(
            user_to_approve_id=self.id
        ).order_by(UserApproval.created_at.desc()).first()
        
        # Determine approval status based on the latest record
        is_approved = latest_approval.is_approved if latest_approval else False
        
        # Update the is_approved field if it's different to stay in sync
        if self.is_approved != is_approved:
            self.is_approved = is_approved
            db.session.add(self)
            db.session.commit()
            
        return is_approved

class UserApproval(db.Model):
    """
    User approval record model.
    
    Tracks approval decisions made by administrators on user accounts.
    Each record represents a single approval or rejection action taken by an admin
    on a specific user account. The model includes an index to efficiently find
    the latest approval status for each user.
    
    Attributes:
        id (int): Primary key identifier for the approval record
        created_at (datetime): Timestamp when the approval decision was made
        is_approved (bool): Whether the user was approved or rejected
        user_admin_id (int): Foreign key to the admin user who made the decision
        user_to_approve_id (int): Foreign key to the user who received the decision
    """
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_approved = db.Column(db.Boolean, nullable=False)  # Approval decision
    user_admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Admin who made the decision
    user_to_approve_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # User being approved/rejected

    # Add an index to efficiently find the latest approval for each user
    __table_args__ = (
        db.Index('idx_latest_approval', user_to_approve_id, created_at.desc()),
    )

class PasswordResetToken(db.Model):
    """
    Password reset token model.
    
    Manages the tokens used in the password reset flow. Each token is associated with
    a specific user, has an expiration date, and tracks whether it has been used.
    Tokens are designed to be used only once and expire after a configurable time period.
    
    Attributes:
        id (int): Primary key identifier for the token
        user_id (int): Foreign key to the user who requested the reset
        token (str): Unique token string for verification
        created_at (datetime): Timestamp when the token was created
        expires_at (datetime): Timestamp when the token expires
        used (bool): Whether the token has been used already
        user (User): Relationship to the User model
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)  # Must be unique
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)  # When the token becomes invalid
    used = db.Column(db.Boolean, default=False, nullable=False)  # Prevents reuse
    
    # Relationship to the user who owns this reset token
    user = db.relationship('User', backref=db.backref('reset_tokens', lazy=True))
    
    @staticmethod
    def generate_token(user_id, expiration_hours=24):
        """
        Generate a new password reset token that expires after the specified hours.
        
        Creates a secure random token for password reset, sets the expiration time,
        saves it to the database, and returns the token object.
        
        Args:
            user_id (int): The ID of the user requesting password reset
            expiration_hours (int, optional): Number of hours until token expires. Defaults to 24.
            
        Returns:
            PasswordResetToken: The newly created token object
        """
        # Create a secure URL-safe token
        token = secrets.token_urlsafe(32)
        # Calculate expiration time
        expires_at = datetime.utcnow() + timedelta(hours=expiration_hours)
        
        # Create the token object
        reset_token = PasswordResetToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        
        # Save to database
        db.session.add(reset_token)
        db.session.commit()
        
        return reset_token
    
    def is_valid(self):
        """
        Check if the token is valid (not expired and not used).
        
        A token is considered valid if it hasn't been used yet and the current time
        is before the expiration time.
        
        Returns:
            bool: True if the token is valid, False otherwise
        """
        now = datetime.utcnow()
        return not self.used and now < self.expires_at
    
    def invalidate(self):
        """
        Mark the token as used to prevent reuse.
        
        Updates the token's used status to True and saves the change to the database.
        This method should be called after a successful password reset.
        
        Returns:
            None
        """
        self.used = True
        db.session.add(self)
        db.session.commit()