"""
Security Forms Module.

This module defines WTForms form classes for handling user authentication and registration.
These forms include field validation and custom validators for business rule enforcement.
"""
from flask_wtf import FlaskForm  # Flask extension for form handling with CSRF protection
from wtforms import StringField, PasswordField  # Form field types
from wtforms.validators import DataRequired, Email, Length, ValidationError  # Field validators
from .models import User  # User model for validation against existing users
from ..schools.models import School  # School model for validation of school existence

class RegistrationForm(FlaskForm):
    """
    User registration form.
    
    This form validates user registration data including personal information,
    email uniqueness, password requirements, and school existence.
    
    Attributes:
        first_name (StringField): User's first name
        last_name (StringField): User's last name
        password (PasswordField): User's password with length validation
        email (StringField): User's email with format validation and uniqueness check
        school_name (StringField): School name that must exist in the database
    """
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, max=50)  # Enforce minimum and maximum password length
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email()  # Validate proper email format
    ])
    school_name = StringField('School', validators=[DataRequired()])

    def validate_email(self, field):
        """
        Custom validator to ensure email uniqueness.
        
        Checks if the provided email is already registered to an active user account.
        
        Args:
            field: The email field to validate
            
        Raises:
            ValidationError: If the email is already registered to an active account
        """
        # Only check for existing active (non-deleted) accounts
        if User.query.filter_by(email=field.data, deleted=False).first():
            raise ValidationError('Email already registered')
            
    def validate_school_name(self, field):
        """
        Custom validator to ensure the school exists.
        
        Checks if the provided school name exists in the database.
        
        Args:
            field: The school_name field to validate
            
        Raises:
            ValidationError: If the school name does not exist in the database
        """
        school = School.query.get(field.data)
        if not school:
            raise ValidationError('Invalid school name')

class LoginForm(FlaskForm):
    """
    User login form.
    
    Simple form for user authentication that validates the email format.
    The actual password validation is handled in the login route.
    
    Attributes:
        username (StringField): User's email address used as the login identifier
    """
    username = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])