"""
Authentication routes for user signup, login, and logout
"""
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError

from src.models import db, User
from src.auth import generate_token, authenticate_user, login_required, get_current_user


auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/signup', methods=['POST'])
def signup():
    """
    Register a new user
    
    Request body:
        {
            "email": "user@example.com",
            "password": "password123",
            "username": "username"
        }
    
    Returns:
        201: User created successfully with token
        400: Invalid request or user already exists
    """
    data = request.get_json()
    
    # Validate required fields
    if not data or not all(k in data for k in ['email', 'password', 'username']):
        return jsonify({
            'error': 'Missing required fields',
            'required': ['email', 'password', 'username']
        }), 400
    
    email = data['email'].strip().lower()
    password = data['password']
    username = data['username'].strip()
    
    # Validate email format
    if '@' not in email or '.' not in email:
        return jsonify({
            'error': 'Invalid email format'
        }), 400
    
    # Validate password length
    if len(password) < 6:
        return jsonify({
            'error': 'Password must be at least 6 characters long'
        }), 400
    
    # Validate username length
    if len(username) < 3:
        return jsonify({
            'error': 'Username must be at least 3 characters long'
        }), 400
    
    try:
        # Create new user
        user = User(
            email=email,
            username=username
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Generate token
        token = generate_token(user.id)
        
        return jsonify({
            'message': 'User created successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'created_at': user.created_at.isoformat()
            },
            'token': token
        }), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            'error': 'User with this email or username already exists'
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to create user',
            'message': str(e)
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login user and return JWT token
    
    Request body:
        {
            "email": "user@example.com",
            "password": "password123"
        }
    
    Returns:
        200: Login successful with token
        400: Invalid request
        401: Invalid credentials
    """
    data = request.get_json()
    
    # Validate required fields
    if not data or not all(k in data for k in ['email', 'password']):
        return jsonify({
            'error': 'Missing required fields',
            'required': ['email', 'password']
        }), 400
    
    email = data['email'].strip().lower()
    password = data['password']
    
    # Authenticate user
    user = authenticate_user(email, password)
    
    if not user:
        return jsonify({
            'error': 'Invalid email or password'
        }), 401
    
    # Generate token
    token = generate_token(user.id)
    
    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': user.id,
            'email': user.email,
            'username': user.username
        },
        'token': token
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout(user):
    """
    Logout user (client-side token removal)
    
    Note: Since we're using stateless JWT, logout is handled client-side
    by removing the token. This endpoint is mainly for consistency.
    
    Returns:
        200: Logout successful
    """
    return jsonify({
        'message': 'Logout successful',
        'note': 'Please remove the token from client storage'
    }), 200


@auth_bp.route('/me', methods=['GET'])
@login_required
def get_profile(user):
    """
    Get current user profile
    
    Returns:
        200: User profile
        401: Not authenticated
    """
    return jsonify({
        'user': {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'created_at': user.created_at.isoformat()
        }
    }), 200


@auth_bp.route('/me', methods=['PUT'])
@login_required
def update_profile(user):
    """
    Update current user profile
    
    Request body:
        {
            "username": "new_username" (optional),
            "password": "new_password" (optional)
        }
    
    Returns:
        200: Profile updated successfully
        400: Invalid request
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': 'No data provided'
        }), 400
    
    try:
        # Update username if provided
        if 'username' in data:
            username = data['username'].strip()
            if len(username) < 3:
                return jsonify({
                    'error': 'Username must be at least 3 characters long'
                }), 400
            user.username = username
        
        # Update password if provided
        if 'password' in data:
            password = data['password']
            if len(password) < 6:
                return jsonify({
                    'error': 'Password must be at least 6 characters long'
                }), 400
            user.set_password(password)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username
            }
        }), 200
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            'error': 'Username already exists'
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to update profile',
            'message': str(e)
        }), 500