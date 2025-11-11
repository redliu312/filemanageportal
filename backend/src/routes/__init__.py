"""
Routes package
"""
from .auth import auth_bp
from .files import files_bp

__all__ = ['auth_bp', 'files_bp']