"""
Slots API Routes Module.

This module provides all the API endpoints for managing enrollment slots, students,
and enrollment records. It includes functionalities for:

- Creating, listing, updating, and deleting slots
- Enrolling students in slots with waiting list support
- Confirming slots and generating confirmation letters
- Managing student data with proper encryption
- Generating statistics and reports

All routes in this blueprint are prefixed with '/api/slots' and require authentication.
Some administrative operations additionally require admin privileges.
"""
from flask import g, jsonify, request, send_file  # Flask web framework components
from app.extensions import db  # Database instance
from app.security.routes import auth  # Authentication functions
from app.security.decorators import admin_required  # Admin authorization decorator
from . import slots  # Blueprint instance
from .models import Slot, StudentEnrollment, TimePeriod, OrganizationInfo, Department, GenderCategory, Student, Gender, User, EnrollmentActivity  # Data models
from datetime import datetime, timedelta, timezone  # Date and time utilities
from sqlalchemy import distinct, and_  # Database query utilities
from io import BytesIO  # For in-memory file operations
import os  # Operating system utilities

# Import utility functions
from ..utils.letter import generate_letters_for_slot  # Document generation
from ..utils.email_utils import send_email, send_slot_confirmation_email  # Email sending

def format_slot(slot):
    """
    Format a Slot model instance into a JSON-serializable dictionary.
    
    This helper function standardizes the conversion of Slot objects to JSON format,
    handling date formatting, enum values, and computed properties like occupied spots.
    
    Args:
        slot (Slot): The Slot model instance to format
        
    Returns:
        dict: A dictionary containing all relevant slot information ready for JSON serialization
    """
    return {
        'id': slot.id,
        'date': slot.date.isoformat() if slot.date else None,  # Format date as ISO string
        'time_period': slot.time_period.value if slot.time_period else None,  # Get enum value string
        'department': slot.department.value if slot.department else None,  # Get enum value string
        'gender_category': slot.gender_category.value if slot.gender_category else None,  # Get enum value string
        'notes': slot.notes,
        'total_spots': slot.total_spots,
        'max_students_per_school': slot.max_students_per_school,
        'is_locked': slot.is_locked,  # Whether slot is locked for modifications
        'is_confirmed': slot.is_confirmed,  # Whether slot is confirmed for attendance
        'created_at': slot.created_at.isoformat() if slot.created_at else None,  # Format timestamp
        'updated_at': slot.updated_at.isoformat() if slot.updated_at else None,  # Format timestamp
        'occupied_spots': slot.get_occupied_spots()  # Get current occupancy count
    }

def format_student(student):
    """
    Format a Student model instance into a JSON-serializable dictionary.
    
    This helper function standardizes the conversion of Student objects to JSON format,
    automatically decrypting sensitive student information stored in the database.
    
    Args:
        student (Student): The Student model instance to format
        
    Returns:
        dict: A dictionary containing student information ready for JSON serialization
    """
    return {
        'id': student.id,
        'first_name': student.first_name,  # Already decrypted by hybrid property
        'last_name': student.last_name,  # Already decrypted by hybrid property
        'school_class': student.school_class,
        'school_name': student.school_name,
        'gender': student.gender if student.gender else None,
        'address': student.address,
        'postal_code': student.postal_code,
        'city': student.city,
        'landline': student.landline,
        'mobile': student.mobile,
        'created_at': student.created_at.isoformat() if student.created_at else None,
        'updated_at': student.updated_at.isoformat() if student.updated_at else None
    }

def format_enrollment(enrollment):
    """
    Format a StudentEnrollment model instance into a JSON-serializable dictionary.
    
    This helper function standardizes the conversion of StudentEnrollment objects to JSON format,
    including nested student information by utilizing the format_student helper.
    
    Args:
        enrollment (StudentEnrollment): The enrollment record to format
        
    Returns:
        dict: A dictionary containing enrollment information ready for JSON serialization
    """
    return {
        'id': enrollment.id,
        'student': format_student(enrollment.student),  # Include formatted student data
        'slot_id': enrollment.slot_id,
        'is_in_waiting_list': enrollment.is_in_waiting_list,  # Waiting list status
        'created_at': enrollment.created_at.isoformat() if enrollment.created_at else None,  # Format timestamp
        'updated_at': enrollment.updated_at.isoformat() if enrollment.updated_at else None  # Format timestamp
    }

def apply_filters(query, filters):
    """
    Apply filtering conditions to a slot query based on provided filters.
    
    This function takes a SQLAlchemy query object and applies various filters
    to narrow down the results based on user-specified criteria. It handles
    date filtering, enum type filtering, and special logic for non-admin users.
    
    Args:
        query: The base SQLAlchemy query object for slots
        filters (dict): A dictionary of filter criteria
        
    Returns:
        The modified SQLAlchemy query with filters applied
        
    Note:
        For non-admin users, slots older than one day are automatically filtered out
    """
    # Apply date filter if present
    if filters.get('date'):
        query = query.filter(Slot.date == datetime.strptime(filters['date'], '%Y-%m-%d').date())
    # Apply time period filter if present (morning/afternoon)
    if filters.get('time_period'):
        query = query.filter(Slot.time_period == filters['time_period'])
    # Apply department filter if present
    if filters.get('department'):
        query = query.filter(Slot.department == filters['department'])
    # Apply gender category filter if present
    if filters.get('gender_category'):
        query = query.filter(Slot.gender_category == filters['gender_category'])
    # Apply locked status filter if present
    if filters.get('is_locked') is not None:
        query = query.filter(Slot.is_locked == filters['is_locked'])
    
    # If user is not admin, hide slots that have passed by more than one day
    if filters.get('is_admin') is False:
        # Get current date minus 1 day as cutoff
        cutoff_date = (datetime.now() - timedelta(days=1)).date()
        query = query.filter(Slot.date > cutoff_date)
        
    return query

def get_pagination_params():
    """
    Extract and prepare pagination parameters from the HTTP request.
    
    This function retrieves and processes query parameters for pagination, sorting,
    and filtering from the current HTTP request. It also determines the admin status
    of the current user to apply appropriate visibility rules.
    
    Returns:
        dict: A dictionary with pagination settings, sorting options, and filter criteria
    """
    # Check if user is logged in and is admin
    is_admin = False
    try:
        # In the Flask-HTTPAuth system, the current user is in auth.current_user()
        if auth.current_user():
            is_admin = auth.current_user().is_admin
    except Exception:
        # If we can't get the user, assume non-admin
        pass
    
    return {
        # Pagination settings
        'page': request.args.get('page', 1, type=int),  # Current page number
        'per_page': request.args.get('per_page', 10, type=int),  # Items per page
        # Sorting settings
        'sort_by': request.args.get('sort_by', 'date'),  # Field to sort by
        'sort_order': request.args.get('sort_order', 'desc'),  # Sort direction (newest first)
        # Filter criteria
        'filters': {
            'date': request.args.get('date'),  # Filter by specific date
            'time_period': request.args.get('time_period'),  # Morning/afternoon
            'department': request.args.get('department'),  # Department filter
            'gender_category': request.args.get('gender_category'),  # Gender category filter
            'is_locked': request.args.get('is_locked', type=lambda x: x.lower() == 'true' if x else None),  # Locked status
            'is_admin': is_admin  # User's admin status for visibility rules
        }
    }

@slots.route('/', methods=['GET'])
@auth.login_required
def get_slots():
    """
    Get a paginated, filtered, and sorted list of enrollment slots.
    
    This endpoint retrieves slots based on query parameters for pagination,
    sorting, and filtering. It returns both the slot data and pagination metadata.
    Non-admin users will not see slots older than one day.
    
    Query Parameters:
        page (int): The page number to retrieve (default: 1)
        per_page (int): Number of items per page (default: 10)
        sort_by (str): Field to sort by (date, time_period, department)
        sort_order (str): Sort direction (asc, desc)
        date (str): Filter by specific date (YYYY-MM-DD format)
        time_period (str): Filter by time period (morning/afternoon)
        department (str): Filter by department
        gender_category (str): Filter by gender category
        is_locked (bool): Filter by locked status
    
    Returns:
        JSON response with slots data and pagination information
    """
    params = get_pagination_params()
    query = Slot.query
    
    query = apply_filters(query, params['filters'])
    
    # Apply sorting - prioritize date sorting for a consistent experience
    if params['sort_by'] == 'date':
        # Default to sorting from future to past
        query = query.order_by(Slot.date.desc() if params['sort_order'] == 'desc' else Slot.date.asc())
    elif params['sort_by'] in ['time_period', 'department', 'created_at']:
        sort_column = getattr(Slot, params['sort_by'])
        query = query.order_by(sort_column.desc() if params['sort_order'] == 'desc' else sort_column)
    
    pagination = query.paginate(page=params['page'], per_page=params['per_page'], error_out=False)
    
    return jsonify({
        'slots': [format_slot(slot) for slot in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev,
        'filters': params['filters'],
        'sort': {'sort_by': params['sort_by'], 'sort_order': params['sort_order']}
    })

@slots.route('/<int:slot_id>', methods=['GET'])
@auth.login_required
def get_slot(slot_id):
    """
    Get detailed information for a specific slot by ID.
    
    This endpoint retrieves a single slot by its ID and returns its details.
    If the slot doesn't exist, it returns a 404 error.
    
    Args:
        slot_id (int): The ID of the slot to retrieve
        
    Returns:
        JSON response with the slot's details
        
    Response:
        200: Returns the slot data
        404: If the slot doesn't exist
    """
    slot = Slot.query.get_or_404(slot_id)
    return jsonify(format_slot(slot))

@slots.route('/enum-values', methods=['GET'])
@auth.login_required
def get_enum_values():
    """
    Get all available enum values used in the slots system.
    
    This endpoint provides the possible values for the various enumerations used
    in the application, such as time periods, departments, gender categories, etc.
    These values are typically used to populate dropdown menus or selection options
    in the frontend.
    
    Returns:
        JSON response with lists of possible values for each enum type
    """
    # Get just the values of the enums without their names
    return jsonify({
        'time_periods': [period.value for period in TimePeriod],
        'departments': [dept.value for dept in Department],
        'gender_categories': [cat.value for cat in GenderCategory]
    })

@slots.route('/', methods=['POST'])
@auth.login_required
@admin_required
def create_slot():
    """
    Create a new enrollment slot.
    
    This endpoint creates a new slot for student enrollments based on the provided data.
    It performs validation to ensure that the slot doesn't conflict with existing slots
    (no more than 2 slots per department per day, and no duplicate time periods).
    This endpoint requires admin privileges.
    
    Request Body:
        date (str): Date of the slot in YYYY-MM-DD format
        time_period (str): Time period (morning/afternoon)
        department (str): Department for the slot
        gender_category (str): Gender category for the slot
        total_spots (int): Total number of available spots
        max_students_per_school (int): Maximum allowed students per school
        notes (str, optional): Additional notes about the slot
        is_locked (bool, optional): Whether the slot is locked for modifications
    
    Returns:
        201: JSON response with the created slot data on success
        400: JSON response with validation error message
        500: JSON response with server error
    """
    data = request.get_json()
    
    try:
        date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        department = Department(data['department'])
        time_period = TimePeriod(data['time_period'])
        
        # First validate total slots per day
        is_valid, error_message = Slot.validate_slots_per_day(date, department)
        if not is_valid:
            return jsonify({'error': error_message.replace(
                "Cannot create more than 2 slots per department per day",
                "Non è possibile creare più di 2 slot per dipartimento al giorno"
            )}), 400
            
        # Then validate time period uniqueness
        is_valid, error_message = Slot.validate_time_period_constraint(date, department, time_period)
        if not is_valid:
            return jsonify({'error': error_message.replace(
                "A slot for",
                "Uno slot per"
            ).replace("already exists on", "esiste già il").replace("during", "durante")}), 400

        slot = Slot(
            date=date,
            time_period=time_period,
            department=department,
            gender_category=GenderCategory(data['gender_category']),
            notes=data.get('notes'),
            total_spots=data['total_spots'],
            max_students_per_school=data['max_students_per_school'],
            is_locked=data.get('is_locked', False)
        )
        
        db.session.add(slot)
        db.session.commit()
        
        return jsonify({
            'message': 'Slot created successfully',
            'slot': format_slot(slot)
        }), 201
        
    except (KeyError, ValueError) as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@slots.route('/<int:slot_id>', methods=['PUT'])
@auth.login_required
@admin_required
def update_slot(slot_id):
    """
    Update an existing enrollment slot by ID.
    
    This endpoint updates the properties of an existing slot based on the provided data.
    Similar to slot creation, it performs validation to ensure the updated slot doesn't
    conflict with existing slots. If only fields that don't affect constraints are changed,
    validation is skipped. This endpoint requires admin privileges.
    
    Args:
        slot_id (int): The ID of the slot to update
    
    Request Body:
        date (str, optional): New date of the slot in YYYY-MM-DD format
        time_period (str, optional): New time period (morning/afternoon)
        department (str, optional): New department for the slot
        gender_category (str, optional): New gender category for the slot
        total_spots (int, optional): New total number of available spots
        max_students_per_school (int, optional): New maximum allowed students per school
        notes (str, optional): New additional notes about the slot
        is_locked (bool, optional): New locked status for the slot
        is_confirmed (bool, optional): New confirmation status for the slot
    
    Returns:
        200: JSON response with the updated slot data on success
        400: JSON response with validation error message
        404: If the slot doesn't exist
        500: JSON response with server error
    """
    slot = Slot.query.get_or_404(slot_id)
    data = request.get_json()
    
    try:
        # If date, department or time_period is being changed, validate constraints
        if any(field in data for field in ['date', 'department', 'time_period']):
            new_date = datetime.strptime(data.get('date', slot.date.strftime('%Y-%m-%d')), '%Y-%m-%d').date()
            new_department = Department(data['department']) if 'department' in data else slot.department
            new_time_period = TimePeriod(data['time_period']) if 'time_period' in data else slot.time_period
            
            # Only validate if any of these fields is actually changing
            if (new_date != slot.date or 
                new_department != slot.department or 
                new_time_period != slot.time_period):
                
                # First validate total slots per day
                is_valid, error_message = Slot.validate_slots_per_day(new_date, new_department, slot_id)
                if not is_valid:
                    return jsonify({'error': error_message.replace(
                        "Cannot create more than 2 slots per department per day",
                        "Non è possibile creare più di 2 slot per dipartimento al giorno"
                    )}), 400
                    
                # Then validate time period uniqueness
                is_valid, error_message = Slot.validate_time_period_constraint(
                    new_date, new_department, new_time_period, slot_id)
                if not is_valid:
                    return jsonify({'error': error_message.replace(
                        "A slot for",
                        "Uno slot per"
                    ).replace("already exists on", "esiste già il").replace("during", "durante")}), 400

        if 'date' in data:
            slot.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        if 'time_period' in data:
            slot.time_period = TimePeriod(data['time_period'])
        if 'department' in data:
            slot.department = Department(data['department'])
        if 'gender_category' in data:
            slot.gender_category = GenderCategory(data['gender_category'])
        if 'notes' in data:
            slot.notes = data['notes']
        if 'total_spots' in data:
            slot.total_spots = data['total_spots']
        if 'max_students_per_school' in data:
            slot.max_students_per_school = data['max_students_per_school']
        if 'is_locked' in data:
            slot.is_locked = data['is_locked']
        if 'is_confirmed' in data:
            slot.is_confirmed = data['is_confirmed']
            
        db.session.commit()
        return jsonify({
            'message': 'Slot updated successfully',
            'slot': format_slot(slot)
        })
        
    except (KeyError, ValueError) as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@slots.route('/<int:slot_id>', methods=['DELETE'])
@auth.login_required
@admin_required
def delete_slot(slot_id):
    """
    Delete an enrollment slot by ID.
    
    This endpoint deletes an existing slot from the system. If the slot has
    any existing enrollments, they will be deleted as well (due to cascade delete).
    This operation cannot be undone. This endpoint requires admin privileges.
    
    Args:
        slot_id (int): The ID of the slot to delete
        
    Returns:
        200: JSON response with success message
        404: If the slot doesn't exist
        500: JSON response with server error
    """
    slot = Slot.query.get_or_404(slot_id)
    
    try:
        # First, delete all enrollments related to this slot
        student_enrollments = StudentEnrollment.query.filter_by(slot_id=slot_id).all()
        for enrollment in student_enrollments:
            db.session.delete(enrollment)
        
        # Then delete the slot itself
        db.session.delete(slot)
        db.session.commit()
        return jsonify({'message': 'Slot deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@slots.route('/available-dates', methods=['GET'])
@auth.login_required
def get_slot_options():
    """
    Get available dates, departments, and time periods for slots.
    
    This endpoint retrieves the distinct dates, departments, and time periods from
    existing slots to populate filter options in the user interface. It helps users
    navigate and filter the available slots effectively.
    
    Returns:
        200: JSON response with lists of available dates, departments, and time periods
    """
    available_dates = db.session.query(distinct(Slot.date)).order_by(Slot.date).all()
    
    return jsonify({
        'available_dates': [date[0].isoformat() for date in available_dates]
    })

@slots.route('/organization-info', methods=['GET'])
@auth.login_required
def get_organization_info():
    """
    Get the organization's contact information.
    
    This endpoint returns the organization's contact details including name,
    telephone, and email. This information is used in various parts of the
    application, including email templates and confirmation letters.
    
    The contact information provided is for Cesare Casaletel, the organization
    representative, and is used in email footers and other communications.
    
    Returns:
        200: JSON response with organization contact details
    """
    return jsonify({
        "first_name": OrganizationInfo.FIRST_NAME.value,
        "last_name": OrganizationInfo.LAST_NAME.value,
        "telephone": OrganizationInfo.TELEPHONE.value,
        "email": OrganizationInfo.EMAIL.value
    })

# Enrollment management routes
@slots.route('/<int:slot_id>/enrollments', methods=['POST'])
@auth.login_required
def create_enrollment(slot_id):
    """
    Enroll a student in a specific slot.
    
    This endpoint creates a new enrollment record for a student in the specified slot.
    It handles various enrollment scenarios including:
    - Creating a new student record if one doesn't exist
    - Automatically determining waiting list status based on available spots
    - Enforcing gender restrictions based on slot gender category
    - Enforcing maximum students per school limitations
    - Tracking enrollment activity for notification emails
    
    Args:
        slot_id (int): The ID of the slot to enroll in
        
    Request Body:
        student (dict): Student information with the following fields:
            first_name (str): Student's first name
            last_name (str): Student's last name
            school_class (str): Student's class name/identifier
            gender (str): Student's gender (Boy/Girl)
            school_name (str): Name of the student's school
            address (str): Student's address
            postal_code (str): Student's postal code
            city (str): Student's city
            mobile (str): Student's or parent's mobile number
            landline (str, optional): Student's or parent's landline number
            
    Returns:
        201: JSON response with the created enrollment record on success
        400: JSON response with validation error message
        404: If the slot doesn't exist
        500: JSON response with server error
    """
    slot = Slot.query.get_or_404(slot_id)
    current_user = auth.current_user()
    
    # Check if slot is locked or confirmed
    if (slot.is_locked or slot.is_confirmed) and not current_user.is_admin:
        return jsonify({'error': 'Non è possibile creare iscrizioni per uno slot bloccato o confermato'}), 403
    
    data = request.get_json()
    try:
        # Check if non-admin user is trying to specify a different school than their own
        if not current_user.is_admin and data.get('school_name') and current_user.school_name and data.get('school_name') != current_user.school_name:
            return jsonify({'error': 'Gli utenti non amministratori possono iscrivere solo studenti della propria scuola'}), 403
            
        # Use current user's school_name if not provided in data
        if not data.get('school_name') and current_user.school_name:
            data['school_name'] = current_user.school_name
            
        # First check if an identical student already exists using decrypted values
        existing_student = None
        if not data.get('student_id'):
            # Iterate through all students and compare decrypted properties
            for s in Student.query.all():
                if (s.first_name.lower() == data['first_name'].lower() and
                    s.last_name.lower() == data['last_name'].lower() and
                    s.school_class.lower() == data['school_class'].lower() and
                    ((s.school_name or '').lower() == (data.get('school_name') or '').lower()) and
                    s.gender == Gender(data['gender']) and
                    s.address.lower() == data['address'].lower() and
                    s.postal_code.lower() == data['postal_code'].lower() and
                    ((s.landline or '').lower() == (data.get('landline') or '').lower()) and
                    s.city.lower() == data['city'].lower() and
                    s.mobile.lower() == data['mobile'].lower()):
                    existing_student = s
                    break

            if existing_student:
                student = existing_student
            else:
                # Create new student if no match found
                student = Student(
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    school_class=data['school_class'],
                    school_name=data.get('school_name'),
                    gender=Gender(data['gender']),
                    address=data['address'],
                    postal_code=data['postal_code'],
                    city=data['city'],
                    landline=data.get('landline'),
                    mobile=data['mobile']
                )
                db.session.add(student)
                db.session.flush()  # Get the student ID without committing
        else:
            student = Student.query.get_or_404(data['student_id'])
            
            # If using an existing student, still enforce the school restriction for non-admins
            if not current_user.is_admin and student.school_name != current_user.school_name and current_user.school_name:
                return jsonify({'error': 'Non-admin users can only enroll students from their own school'}), 403
        
        # Check if student is already enrolled in this slot
        existing_enrollment = StudentEnrollment.query.filter_by(
            student_id=student.id,
            slot_id=slot_id
        ).first()
        if existing_enrollment:
            return jsonify({'error': 'Lo studente è già iscritto a questo slot'}), 400
            
        # Check if student's gender is allowed in this slot
        if not slot.can_enroll_student(student):
            return jsonify({'error': 'GENERE_NON_CONSENTITO'}), 400
            
        # Check available spots
        available_spots = slot.total_spots - slot.get_occupied_spots()
        print(f"Available spots: {available_spots}")
        
        # Initialize waiting list status
        data['is_in_waiting_list'] = False
        
        # Put in waiting list if no spots or school limit reached
        if available_spots <= 0:
            data['is_in_waiting_list'] = True
        elif not current_user.is_admin:
            # School limit check for non-admin users
            max_allowed = min(slot.max_students_per_school, available_spots)
            school_count = slot.get_school_enrollment_count(student.school_name)
            
            if school_count >= slot.max_students_per_school:
                data['is_in_waiting_list'] = True

        # If admin is creating the enrollment, try to find the first non-admin user from the student's school
        creator_user = current_user
        if current_user.is_admin and student.school_name:
            try:
                school_user = User.query.filter(
                    User.school_name == student.school_name,
                    User.is_admin == False
                ).first()
                if school_user:
                    creator_user = school_user
            except Exception as e:
                print(f"Error finding school user: {str(e)}")

        # Use the factory method to create enrollment with the determined user 
        enrollment = StudentEnrollment.create(slot, student, creator_user)
        enrollment.is_in_waiting_list = data['is_in_waiting_list']
        
        # Ensure slot is marked as unconfirmed when enrollment changes
        slot.is_confirmed = False
        
        db.session.add(enrollment)

        # Update activity tracking for non-admin users
        if not current_user.is_admin:
            # Update last activity time
            EnrollmentActivity.update_activity(current_user.id)

        db.session.commit()

        # Check for pending summaries after commit to ensure activity is saved
        if not current_user.is_admin:
            EnrollmentActivity.check_and_send_summaries()
        
        return jsonify({
            'message': 'Enrollment created successfully',
            'enrollment': format_enrollment(enrollment)
        }), 201
        
    except (KeyError, ValueError) as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@slots.route('/enrollments/<int:enrollment_id>', methods=['DELETE'])
@auth.login_required
def delete_enrollment(enrollment_id):
    enrollment = StudentEnrollment.query.get_or_404(enrollment_id)
    
    # Check if slot is locked
    if enrollment.slot.is_locked and not auth.current_user().is_admin:
        return jsonify({'error': 'Non è possibile eliminare iscrizioni da uno slot bloccato'}), 403
    
    # Check if user is admin or if they created the enrollment
    if not auth.current_user().is_admin and enrollment.user_id != auth.current_user().id:
        return jsonify({'error': 'Non autorizzato a eliminare questa iscrizione'}), 403
    
    try:
        # Set slot as unconfirmed before deleting enrollment
        enrollment.slot.is_confirmed = False
        db.session.delete(enrollment)
        db.session.commit()
        return jsonify({'message': 'Enrollment deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@slots.route('/enrollments/<int:enrollment_id>/waiting-list', methods=['PUT'])
@auth.login_required
def update_enrollment_waiting_list(enrollment_id):
    """
    Move a student between regular enrollment and waiting list.
    
    This endpoint toggles the waiting list status of an enrollment. It can move a
    student from the waiting list to regular enrollment or vice versa. This operation
    can only be performed by administrators and is useful for manually managing
    enrollment priorities.
    
    Args:
        enrollment_id (int): The ID of the enrollment record to update
        
    Request Body:
        is_in_waiting_list (bool): New waiting list status for the enrollment
        
    Returns:
        200: JSON response with the updated enrollment record
        400: JSON response with error message if validation fails
        404: If the enrollment doesn't exist
        500: JSON response with server error
    """
    enrollment = StudentEnrollment.query.get_or_404(enrollment_id)
    slot = enrollment.slot
    current_user = auth.current_user()
    
    # Check if slot is locked or confirmed
    if (slot.is_locked or slot.is_confirmed) and not current_user.is_admin:
        return jsonify({'error': 'Non è possibile aggiornare iscrizioni in uno slot bloccato o confermato'}), 403
    
    # Check if user is admin or if they created the enrollment
    if not current_user.is_admin and enrollment.user_id != current_user.id:
        return jsonify({'error': 'Non autorizzato a modificare questa iscrizione'}), 403
    
    data = request.get_json()
    try:
        is_in_waiting_list = data['is_in_waiting_list']
        
        # If moving from waiting list to registered, check capacity
        if not is_in_waiting_list and enrollment.is_in_waiting_list:
            # First get available spots
            available_spots = slot.total_spots - slot.get_occupied_spots() 
            print(f"Available spots: {available_spots}")
            
            # Only check total spots limit for everyone (including admins)
            if available_spots <= 0:
                return jsonify({'error': 'Nessun posto disponibile in totale'}), 400
            
            # School limit check - only for non-admin users
            if not current_user.is_admin:
                # A school can't have more students than the available spots
                max_allowed = min(slot.max_students_per_school, available_spots)
                print(f"Max allowed: {max_allowed}")

                # Now check this specific school's current count
                school_count = slot.get_school_enrollment_count(enrollment.student.school_name)

                print(f"School count: {school_count}")
                if max_allowed < 1: 
                    return jsonify({'error': 'Limite di capacità della scuola raggiunto'}), 400
                
            # For admins, we bypass the school limit check but still respect total available spots
        
        enrollment.is_in_waiting_list = is_in_waiting_list
        # Ensure slot is marked as unconfirmed when enrollment status changes
        slot.is_confirmed = False
        db.session.commit()
        
        return jsonify({
            'message': 'Enrollment waiting list status updated successfully',
            'enrollment': format_enrollment(enrollment)
        })
        
    except (KeyError, ValueError) as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@slots.route('/<int:slot_id>/enrollments', methods=['GET'])
@auth.login_required
def get_slot_enrollments(slot_id):
    is_waiting_list = request.args.get('is_waiting_list', type=lambda x: x.lower() == 'true')
    
    query = StudentEnrollment.query.filter_by(slot_id=slot_id)
    
    # Filter by waiting list status if specified
    if is_waiting_list is not None:
        query = query.filter_by(is_in_waiting_list=is_waiting_list)
    
    # If not admin, only show user's enrollments
    if not auth.current_user().is_admin:
        query = query.filter_by(user_id=auth.current_user().id)
    
    enrollments = query.all()
    
    return jsonify({
        'enrollments': [format_enrollment(enrollment) for enrollment in enrollments]
    })

@slots.route('/students/<int:student_id>', methods=['PUT'])
@auth.login_required
def update_student(student_id):
    """
    Update a student's information.
    
    This endpoint updates the personal information for an existing student record.
    It handles data validation and encrypts sensitive student information before
    storing it in the database. When a student record is updated, any associated
    slot confirmation status is reset to trigger re-verification.
    
    Args:
        student_id (int): The ID of the student to update
        
    Request Body:
        first_name (str, optional): Student's updated first name
        last_name (str, optional): Student's updated last name
        school_class (str, optional): Student's updated class name/identifier
        gender (str, optional): Student's updated gender
        school_name (str, optional): Updated name of the student's school
        address (str, optional): Student's updated address
        postal_code (str, optional): Student's updated postal code
        city (str, optional): Student's updated city
        mobile (str, optional): Student's updated mobile number
        landline (str, optional): Student's updated landline number
        
    Returns:
        200: JSON response with the updated student record
        400: JSON response with validation error message
        404: If the student doesn't exist
        500: JSON response with server error
    """
    student = Student.query.get_or_404(student_id)
    current_user = auth.current_user()
    
    # Check if user is admin or if they have any enrollments with this student
    if not current_user.is_admin:
        # Only check if user manages this student
        enrollment = StudentEnrollment.query.filter_by(
            student_id=student_id,
            user_id=current_user.id
        ).first()
        if not enrollment:
            return jsonify({'error': 'Non autorizzato a modificare questo studente'}), 403
    
    data = request.get_json()
    try:
        # Check if non-admin user is trying to specify a different school than their own
        if not current_user.is_admin and data.get('school_name') and current_user.school_name and data.get('school_name') != current_user.school_name:
            return jsonify({'error': 'Gli utenti non amministratori possono assegnare studenti solo alla propria scuola'}), 403
            
        # Use current user's school_name if not provided in data
        if not data.get('school_name') and current_user.school_name:
            data['school_name'] = current_user.school_name
            
        # Check if these changes would create a duplicate student
        potential_duplicate = Student.query.filter(
            Student.id != student_id,  # Exclude current student
            db.func.lower(Student.first_name) == db.func.lower(data.get('first_name', student.first_name)),
            db.func.lower(Student.last_name) == db.func.lower(data.get('last_name', student.last_name)),
            db.func.lower(Student.school_class) == db.func.lower(data.get('school_class', student.school_class)),
            db.func.lower(Student.school_name) == db.func.lower(data.get('school_name', student.school_name)) if data.get('school_name', student.school_name) else Student.school_name.is_(None),
            Student.gender == data.get('gender', student.gender),
            db.func.lower(Student.address) == db.func.lower(data.get('address', student.address)),
            db.func.lower(Student.postal_code) == db.func.lower(data.get('postal_code', student.postal_code)),
            db.func.lower(Student.city) == db.func.lower(data.get('city', student.city)),
            ((db.func.lower(Student.landline) == db.func.lower(data.get('landline', student.landline))) if data.get('landline', student.landline)
             else Student.landline.is_(None)),
            db.func.lower(Student.mobile) == db.func.lower(data.get('mobile', student.mobile))
        ).first()

        if potential_duplicate:
            # If we found a duplicate, we'll merge the enrollments into the existing student
            # Get all enrollments for the current student
            enrollments = StudentEnrollment.query.filter_by(student_id=student_id).all()
            
            # Update each enrollment to use the duplicate student ID
            for enrollment in enrollments:
                # Check if an enrollment already exists for this slot with the duplicate student
                existing_enrollment = StudentEnrollment.query.filter_by(
                    student_id=potential_duplicate.id,
                    slot_id=enrollment.slot_id
                ).first()
                
                if not existing_enrollment:
                    # If no enrollment exists, update this one to use the duplicate student
                    enrollment.student_id = potential_duplicate.id
                else:
                    # If an enrollment already exists, delete this one
                    db.session.delete(enrollment)
            
            # Delete the current student since all enrollments have been moved
            db.session.delete(student)
            db.session.commit()
            
            return jsonify({
                'message': 'Student merged with existing identical student',
                'student': format_student(potential_duplicate)
            })
            
        # If no duplicate found, proceed with the update
        if 'first_name' in data:
            student.first_name = data['first_name']
        if 'last_name' in data:
            student.last_name = data['last_name']
        if 'school_class' in data:
            student.school_class = data['school_class']
        if 'school_name' in data:
            student.school_name = data['school_name']
        if 'gender' in data:
            student.gender = Gender(data['gender'])
        if 'address' in data:
            student.address = data['address']
        if 'postal_code' in data:
            student.postal_code = data['postal_code']
        if 'city' in data:
            student.city = data['city']
        if 'landline' in data:
            student.landline = data['landline']
        if 'mobile' in data:
            student.mobile = data['mobile']
            
        db.session.commit()
        return jsonify({
            'message': 'Student updated successfully',
            'student': format_student(student)
        })
        
    except (KeyError, ValueError) as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@slots.route('/<int:slot_id>/generate-letters', methods=['GET'])
@auth.login_required
@admin_required
def get_slot_letters(slot_id):
    """
    Generate and download confirmation letters for a slot.
    
    This endpoint generates confirmation letters for all students enrolled in the
    specified slot (not in waiting list) and returns them as a downloadable file.
    The letters are generated based on department-specific templates and include
    student and slot information. This endpoint requires admin privileges.
    
    Args:
        slot_id (int): The ID of the slot to generate letters for
        
    Returns:
        200: Downloadable file with the generated letters
        404: If the slot doesn't exist
        500: JSON response with error message if generation fails
    """
    try:
        pdf_content = generate_letters_for_slot(slot_id)
        
        if pdf_content is None:
            return jsonify({"message": "No active enrollments found for this slot"}), 404
            
        return send_file(
            BytesIO(pdf_content),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'letters_slot_{slot_id}.pdf'
        )
            
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        print(str(e))
        return jsonify({"error": "Failed to generate letters " + str(e)}), 500

@slots.route('/<int:slot_id>/confirm', methods=['POST'])
@auth.login_required
@admin_required
def confirm_slot(slot_id):
    """
    Confirm a slot and send confirmation emails to enrolled students.
    
    This endpoint marks a slot as confirmed and triggers the sending of confirmation
    emails to all students enrolled in the slot (not in waiting list). It also generates
    confirmation letters for each student that will be attached to the emails.
    This operation can only be performed by administrators.
    
    Args:
        slot_id (int): The ID of the slot to confirm
        
    Returns:
        200: JSON response with success message and list of student emails
        400: JSON response with error message if validation fails
        404: If the slot doesn't exist
        500: JSON response with server error message
    """
    slot = Slot.query.get_or_404(slot_id)
    
    try:
        # First confirm the slot
        slot.is_confirmed = True
        db.session.commit()
        
        # Get all non-waitlist enrollments for this slot
        enrollments = StudentEnrollment.query.filter_by(
            slot_id=slot_id,
            is_in_waiting_list=False
        ).all()
        
        # Group students by school and collect associated users
        school_data = {}
        for enrollment in enrollments:
            school_name = enrollment.student.school_name
            if school_name not in school_data:
                # Get all non-admin users associated with this school
                school_users = User.query.filter_by(
                    school_name=school_name,
                    is_admin=False
                ).all()
                
                school_data[school_name] = {
                    'students': [],
                    'users': school_users
                }
            school_data[school_name]['students'].append(enrollment.student)
        
        # Send emails to each school's users
        for school_name, data in school_data.items():
            if not data['users']:  # Skip if no users found for school
                continue
            
            # Prepare slot information for email
            slot_info = {
                'date': slot.date,
                'time_period': slot.time_period.value,
                'department': slot.department.value,
                'gender_category': slot.gender_category.value,
                'students': [{
                    'name': f"{student.first_name} {student.last_name}",
                    'class': student.school_class
                } for student in data['students']]
            }
            
            # Send HTML-formatted email to each user of the school using modern template
            for user in data['users']:
                # Get user's full name for the greeting
                user_name = f"{user.first_name} {user.last_name}"
                
                # Send using the new HTML template function
                send_slot_confirmation_email(
                    student_email=user.email,
                    user_full_name=user_name,
                    slot_info=slot_info
                )
        
        return jsonify({
            'message': 'Slot confirmed and notification emails sent successfully',
            'slot': format_slot(slot)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

