from flask import jsonify, request
from app.security.models import User, UserApproval
from app.extensions import db
from app.security.routes import auth
from app.security.decorators import admin_required
from . import user_management
from werkzeug.security import generate_password_hash
from sqlalchemy import desc, and_, exists
from app.utils.email_utils import send_account_approval_email

def apply_filters(query, filters):
    if filters.get('school_name'):
        query = query.filter(User.school_name == filters['school_name'])
    if filters.get('is_admin') is not None:
        query = query.filter(User.is_admin == filters['is_admin'])
    if filters.get('is_active') is not None:
        query = query.filter(User.is_active == filters['is_active'])
    if filters.get('is_approved') is not None:
        query = query.filter(User.is_approved == filters['is_approved'])
    return query

def apply_search(query, search):
    if search:
        search_term = f"%{search}%"
        return query.filter(db.or_(
            User.email.ilike(search_term),
            User.first_name.ilike(search_term),
            User.last_name.ilike(search_term)
        ))
    return query

def apply_sorting(query, sort_by, sort_order):
    if sort_by in ['id', 'email', 'first_name', 'last_name', 'school_name', 'created_at']:
        sort_column = getattr(User, sort_by)
        return query.order_by(sort_column.desc() if sort_order == 'desc' else sort_column)
    return query

def get_pagination_params():
    return {
        'page': request.args.get('page', 1, type=int),
        'per_page': request.args.get('per_page', 10, type=int),
        'sort_by': request.args.get('sort_by', 'id'),
        'sort_order': request.args.get('sort_order', 'asc'),
        'search': request.args.get('search', '').strip(),
        'filters': {
            'school_name': request.args.get('school_name'),
            'is_admin': request.args.get('is_admin', type=lambda x: x.lower() == 'true'),
            'is_active': request.args.get('is_active', type=lambda x: x.lower() == 'true'),
            'is_approved': request.args.get('is_approved', type=lambda x: x.lower() == 'true'),
        }
    }

def format_user_list(users):
    return [{
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_admin': user.is_admin,
        'is_active': user.is_active,
        'is_approved': user.is_approved,
        'school_name': user.school_name,
        'created_at': user.created_at.isoformat() if user.created_at else None
    } for user in users]

@user_management.route('/users', methods=['GET'])
@auth.login_required
@admin_required
def get_users():
    """
    Retrieve a paginated list of all users in the system.
    
    This endpoint returns all users (not deleted) with pagination, sorting, and filtering
    capabilities. It is restricted to administrators and provides comprehensive user
    information for management purposes.
    
    Query Parameters:
        page (int): Page number for pagination (default: 1)
        per_page (int): Number of items per page (default: 10)
        sort_by (str): Field to sort by (default: 'id')
        sort_order (str): 'asc' or 'desc' (default: 'asc')
        search (str): Search term for filtering by name or email
        school_name (str): Filter by school name
        is_admin (bool): Filter by admin status
        is_active (bool): Filter by active status
        is_approved (bool): Filter by approval status
        
    Returns:
        200: JSON response with paginated user list and metadata
        401: If authentication fails
        403: If the user isn't an administrator
    """
    params = get_pagination_params()
    query = User.query.filter_by(deleted=False)
    
    query = apply_filters(query, params['filters'])
    query = apply_search(query, params['search'])
    query = apply_sorting(query, params['sort_by'], params['sort_order'])
    
    pagination = query.paginate(page=params['page'], per_page=params['per_page'], error_out=False)
    
    return jsonify({
        'users': format_user_list(pagination.items),
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev,
        'filters': params['filters'],
        'sort': {'sort_by': params['sort_by'], 'sort_order': params['sort_order']}
    })

@user_management.route('/users/approved', methods=['GET'])
@auth.login_required
@admin_required
def get_approved_users():
    """
    Retrieve a paginated list of approved users in the system.
    
    This endpoint returns only users who have been approved (either admin users or
    those with approved status). It includes pagination, sorting, and filtering
    capabilities and is restricted to administrators.
    
    The endpoint uses complex SQL queries with subqueries to determine the latest
    approval status for each user, ensuring accurate results.
    
    Query Parameters:
        page (int): Page number for pagination (default: 1)
        per_page (int): Number of items per page (default: 10)
        sort_by (str): Field to sort by (default: 'id')
        sort_order (str): 'asc' or 'desc' (default: 'asc')
        search (str): Search term for filtering by name or email
        school_name (str): Filter by school name
        is_admin (bool): Filter by admin status
        is_active (bool): Filter by active status
        is_approved (bool): Filter by approval status
        
    Returns:
        200: JSON response with paginated approved user list and metadata
        401: If authentication fails
        403: If the user isn't an administrator
    """
    params = get_pagination_params()
    
    # First get the latest approval for each user using a subquery
    latest_approval_dates = db.session.query(
        UserApproval.user_to_approve_id,
        db.func.max(UserApproval.created_at).label('max_created_at')
    ).group_by(UserApproval.user_to_approve_id).subquery()
    
    # Join with UserApproval to get the approval status
    latest_approvals = db.session.query(
        UserApproval.user_to_approve_id,
        UserApproval.is_approved
    ).join(
        latest_approval_dates,
        db.and_(
            UserApproval.user_to_approve_id == latest_approval_dates.c.user_to_approve_id,
            UserApproval.created_at == latest_approval_dates.c.max_created_at
        )
    ).subquery()
    
    # Main query
    query = User.query.outerjoin(
        latest_approvals,
        User.id == latest_approvals.c.user_to_approve_id
    ).filter(
        db.and_(
            User.deleted == False,
            db.or_(
                User.is_admin == True,
                latest_approvals.c.is_approved == True
            )
        )
    )
    
    query = apply_filters(query, params['filters'])
    query = apply_search(query, params['search'])
    query = apply_sorting(query, params['sort_by'], params['sort_order'])
    
    pagination = query.paginate(page=params['page'], per_page=params['per_page'], error_out=False)
    
    return jsonify({
        'users': format_user_list(pagination.items),
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev,
        'filters': params['filters'],
        'sort': {'sort_by': params['sort_by'], 'sort_order': params['sort_order']}
    })

@user_management.route('/users/pending', methods=['GET'])
@auth.login_required
@admin_required
def get_pending_users():
    """
    Retrieve a paginated list of pending users awaiting approval.
    
    This endpoint returns only users who have registered but have not yet received
    an approval decision. It includes pagination, sorting, and filtering capabilities
    and is restricted to administrators who need to review and approve new users.
    
    Query Parameters:
        page (int): Page number for pagination (default: 1)
        per_page (int): Number of items per page (default: 10)
        sort_by (str): Field to sort by (default: 'id')
        sort_order (str): 'asc' or 'desc' (default: 'asc')
        search (str): Search term for filtering by name or email
        school_name (str): Filter by school name
        is_admin (bool): Filter by admin status
        is_active (bool): Filter by active status
        is_approved (bool): Filter by approval status
        
    Returns:
        200: JSON response with paginated pending user list and metadata
        401: If authentication fails
        403: If the user isn't an administrator
    """
    params = get_pagination_params()
    
    query = User.query.filter(
        db.and_(
            User.deleted == False,
            User.is_admin == False,
            User.is_approved == False,
            ~exists().where(UserApproval.user_to_approve_id == User.id)
        )
    )
    
    query = apply_filters(query, params['filters'])
    query = apply_search(query, params['search'])
    query = apply_sorting(query, params['sort_by'], params['sort_order'])
    
    pagination = query.paginate(page=params['page'], per_page=params['per_page'], error_out=False)
    
    return jsonify({
        'users': format_user_list(pagination.items),
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev,
        'filters': params['filters'],
        'sort': {'sort_by': params['sort_by'], 'sort_order': params['sort_order']}
    })

@user_management.route('/users/<int:user_id>', methods=['GET'])
@auth.login_required
def get_user(user_id):
    """
    Retrieve detailed information about a specific user.
    
    This endpoint returns detailed information about a user, including their
    approval history. Users can only access their own information, while
    administrators can access information for any user.
    
    Args:
        user_id (int): The ID of the user to retrieve
        
    Returns:
        200: JSON response with detailed user information
        401: If authentication fails
        403: If a non-admin user tries to access another user's information
        404: If the user doesn't exist
    """
    current_user = auth.current_user()
    if not current_user.is_admin and current_user.id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    user = User.query.get_or_404(user_id)
    
    return jsonify({
        **format_user_list([user])[0],
        'deleted': user.deleted,
        'approval_history': [{
            'created_at': approval.created_at.isoformat(),
            'is_approved': approval.is_approved,
            'admin_email': approval.admin_user.email
        } for approval in user.approvals_received]
    })

@user_management.route('/users/<int:user_id>', methods=['PUT'])
@auth.login_required
def update_user(user_id):
    """
    Update information for a specific user.
    
    This endpoint allows users to update their own information or administrators
    to update any user's information. It handles field validation and ensures
    proper access control. Administrators can additionally update special fields
    like admin status and active status.
    
    Args:
        user_id (int): The ID of the user to update
        
    Request Body (JSON):
        first_name (str, optional): User's updated first name
        last_name (str, optional): User's updated last name
        email (str, optional): User's updated email address
        school_name (str, optional): User's updated school name
        password (str, optional): User's updated password
        is_admin (bool, optional): Admin status (admin only)
        is_active (bool, optional): Active status (admin only)
        
    Returns:
        200: JSON response with the updated user information
        400: JSON response with validation errors
        401: If authentication fails
        403: If a non-admin user tries to update another user or restricted fields
        404: If the user doesn't exist
    """
    current_user = auth.current_user()
    if not current_user.is_admin and current_user.id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    updatable_fields = ['email', 'first_name', 'last_name', 'school_name']
    if current_user.is_admin:
        updatable_fields.extend(['is_admin', 'is_active'])
    
    for field in updatable_fields:
        if field in data:
            setattr(user, field, data[field])
    
    if 'password' in data:
        user.password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    
    try:
        db.session.commit()
        return jsonify({'message': 'User updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@user_management.route('/users/<int:user_id>', methods=['DELETE'])
@auth.login_required
@admin_required
def delete_user(user_id):
    """
    Soft delete a user from the system.
    
    This endpoint marks a user as deleted in the database rather than actually
    removing the record. This preserves historical data while preventing the user
    from logging in. This operation can only be performed by administrators.
    
    Args:
        user_id (int): The ID of the user to delete
        
    Returns:
        200: JSON response with success message
        401: If authentication fails
        403: If the user isn't an administrator
        404: If the user doesn't exist
    """
    user = User.query.get_or_404(user_id)
    if user.id == auth.current_user().id:
        return jsonify({'error': 'Cannot delete yourself'}), 400
    
    user.deleted = True
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})

@user_management.route('/users/approve/<int:user_id>', methods=['POST'])
@auth.login_required
@admin_required
def approve_user(user_id):
    """
    Approve or reject a user's account registration.
    
    This endpoint handles the user approval workflow, allowing administrators to
    either approve or reject user account requests. It creates an approval record,
    updates the user's approval status, and sends a notification email to the user.
    
    The email notification uses the modern HTML template system with styled headers,
    responsive design, login buttons for direct access, and organization contact 
    information in the footer (Cesare Casaletel's contact details).
    
    Args:
        user_id (int): The ID of the user to approve or reject
        
    Request Body (JSON):
        is_approved (bool): Whether to approve (true) or reject (false) the user
        
    Returns:
        200: JSON response with success message
        400: JSON response with error if required fields are missing
        401: If authentication fails
        403: If the user isn't an administrator
        404: If the user doesn't exist
    """
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 415

    user = User.query.get_or_404(user_id)
    is_approved = request.get_json().get('is_approved', True)
    user.is_approved = is_approved
    
    approval = UserApproval(
        user_admin_id=auth.current_user().id,
        user_to_approve_id=user_id,
        is_approved=is_approved
    )
    
    db.session.add(approval)
    db.session.commit()


    if is_approved:
        send_account_approval_email(user.email, f"{user.first_name} {user.last_name}")
    
    
    return jsonify({
        'message': f'User {"approved" if is_approved else "rejected"} successfully',
        'approval': {
            'id': approval.id,
            'created_at': approval.created_at.isoformat(),
            'is_approved': approval.is_approved,
            'admin_id': auth.current_user().id
        }
    })

@user_management.route('/users/<int:user_id>/activate', methods=['POST'])
@auth.login_required
@admin_required
def activate_user(user_id):
    """
    Activate or deactivate a user's account.

    This endpoint allows administrators to activate or deactivate a user's account.
    It updates the user's active status and returns a success message.

    Args:
        user_id (int): The ID of the user to activate or deactivate

    Request Body (JSON):
        is_active (bool): Whether to activate (true) or deactivate (false) the user

    Returns:
        200: JSON response with success message
        400: JSON response with error if required fields are missing
        401: If authentication fails
        403: If the user isn't an administrator
        404: If the user doesn't exist
    """
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'is_active' not in data:
        return jsonify({'error': 'is_active field is required'}), 400
    
    user.is_active = data['is_active']
    db.session.commit()
    return jsonify({'message': f'User {"activated" if user.is_active else "deactivated"} successfully'})