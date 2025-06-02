"""
Schools API routes module.

This module contains all the API endpoints for creating, reading, updating,
and deleting school entities in the system. Access to modifying operations
requires administrative privileges.
"""
from flask import jsonify, request
from . import schools  # Blueprint instance
from .models import School  # School data model
from ..extensions import db  # Database instance
from ..security.decorators import admin_required  # Admin-level access control decorator
# Import auth at function level to avoid circular imports

@schools.route('/', methods=['GET'])
def get_schools():
    """
    Get a list of all registered schools in the system.
    
    Returns:
        JSON response with the list of school names.
    """
    schools_list = School.query.all()
    return jsonify({
        'schools': [school.name for school in schools_list]
    })

@schools.route('/<string:name>', methods=['GET'])
def get_school(name):
    """
    Get details for a specific school by name.
    
    Args:
        name (str): The name of the school to retrieve.
        
    Returns:
        JSON response with the school name, or 404 if not found.
    """
    school = School.query.get_or_404(name)
    return jsonify({'name': school.name})

@schools.route('/', methods=['POST'])
@admin_required
def create_school():
    """
    Create a new school in the system.
    
    This endpoint is protected by the admin_required decorator, ensuring only
    administrators can create new schools.
    
    Request body:
        JSON with the following fields:
        - name (str): Name of the school to create
        
    Returns:
        JSON response with success or error message:
        - 201: School created successfully, returns school name
        - 400: Invalid request data or database error
    """
    data = request.get_json()
    name = data.get('name')
    
    if not name:
        return jsonify({'error': 'School name is required'}), 400
        
    if School.query.get(name):
        return jsonify({'error': 'School already exists'}), 400
        
    school = School(name=name)
    try:
        db.session.add(school)
        db.session.commit()
        return jsonify({'message': 'School created successfully', 'name': school.name}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@schools.route('/<string:name>', methods=['PUT'])
@admin_required
def update_school(name):
    """
    Update an existing school by name.
    
    This endpoint is protected by the admin_required decorator, ensuring only
    administrators can update school information.
    
    Args:
        name (str): The current name of the school to update.
    
    Request body:
        JSON with the following fields:
        - name (str): New name for the school
        
    Returns:
        JSON response with success or error message:
        - 200: School updated successfully, returns new name
        - 400: Invalid request data or database error
        - 404: School not found
    """
    school = School.query.get_or_404(name)
    data = request.get_json()
    new_name = data.get('name')
    
    if not new_name:
        return jsonify({'error': 'New school name is required'}), 400
        
    if School.query.get(new_name) and new_name != name:
        return jsonify({'error': 'A school with this name already exists'}), 400
        
    try:
        # Since name is the primary key, we need to create a new record and delete the old one
        new_school = School(name=new_name)
        db.session.add(new_school)
        db.session.delete(school)
        db.session.commit()
        return jsonify({'message': 'School updated successfully', 'name': new_name})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@schools.route('/<string:name>', methods=['DELETE'])
@admin_required
def delete_school(name):
    """
    Delete a school from the system by name.
    
    This endpoint is protected by the admin_required decorator, ensuring only
    administrators can delete schools.
    
    Args:
        name (str): The name of the school to delete.
        
    Returns:
        JSON response with success or error message:
        - 200: School deleted successfully
        - 400: Database error during deletion
        - 404: School not found
    """
    school = School.query.get_or_404(name)
    try:
        db.session.delete(school)
        db.session.commit()
        return jsonify({'message': 'School deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400