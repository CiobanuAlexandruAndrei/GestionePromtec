"""
School models module.

This module defines the data models for schools in the system.
It contains a simple School model with a name primary key.
"""
from ..extensions import db  # Database instance for ORM

class School(db.Model):
    """
    School model representing educational institutions in the system.
    
    This is a simple model with just a name field that serves as the primary key.
    Schools are referenced by enrollment slots and other parts of the application.
    
    Attributes:
        name (str): The name of the school, serves as the primary key (max 50 chars)
    """
    name = db.Column(db.String(50), primary_key=True)  # School name as primary key