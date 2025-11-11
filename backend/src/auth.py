"""
Authentication utilities for JWT token management
"""
import os
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Dict, Any

import jwt
from flask import request, jsonify
from werkzeug.security import check_password_hash

from src.models import db, User


def generate_token(user_id: int, expires_in: int = 86400) -> str:
    """
    Generate JWT token for user
    
    Args:
        user_id: User ID
        expires_in: Token expiration time in seconds (default: 24 hours)
    
    Returns:
        JWT token string
    """
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(seconds=expires_in),
        'iat': datetime.utcnow()
    }
    
    secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')
    return jwt.encode(payload, secret_key, algorithm='HS256')


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded payload or None if invalid
    """
    try:
        secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_current_user() -> Optional[User]:
    """
    Get current user from request token
    
    Returns:
        User object or None if not authenticated
    """
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    payload = decode_token(token)
    
    if not payload:
        return None
    
    user = db.session.get(User, payload['user_id'])
    return user


def login_required(f):
    """
    Decorator to require authentication for routes
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        
        if not user:
            return jsonify({
                'error': 'Authentication required',
                'message': 'Please provide a valid token'
            }), 401
        
        return f(user, *args, **kwargs)
    
    return decorated_function


def authenticate_user(email: str, password: str) -> Optional[User]:
    """
    Authenticate user with email and password
    
    Args:
        email: User email
        password: User password
    
    Returns:
        User object if authenticated, None otherwise
    """
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return None
    
    return user