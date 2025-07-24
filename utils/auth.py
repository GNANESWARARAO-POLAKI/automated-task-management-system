"""
Authentication Service for Task Manager API
Handles user authentication, session management, and security
"""

import jwt
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import wraps
from flask import request, jsonify, current_app
import logging

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.algorithm = 'HS256'
        self.token_expiry = timedelta(hours=24)  # Token expires in 24 hours
    
    def generate_token(self, user) -> str:
        """Generate JWT token for user"""
        try:
            payload = {
                'user_id': user.id,
                'email': user.email,
                'name': user.name,
                'exp': datetime.utcnow() + self.token_expiry,
                'iat': datetime.utcnow()
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            logger.info(f"Generated token for user: {user.email}")
            return token
            
        except Exception as e:
            logger.error(f"Error generating token: {str(e)}")
            raise
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}")
            return None
    
    def extract_token_from_request(self) -> Optional[str]:
        """Extract token from request headers"""
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header.split(' ')[1]
        return None
    
    def get_current_user_from_token(self) -> Optional[Dict[str, Any]]:
        """Get current user info from token in request"""
        token = self.extract_token_from_request()
        if token:
            return self.verify_token(token)
        return None

# Global auth service instance
auth_service = AuthService()

def require_auth(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            user_data = auth_service.get_current_user_from_token()
            if not user_data:
                return jsonify({
                    'success': False,
                    'error': 'Authentication required',
                    'timestamp': datetime.now().isoformat()
                }), 401
            
            # Add user info to request context
            request.current_user = user_data
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Authentication failed',
                'timestamp': datetime.now().isoformat()
            }), 401
    
    return decorated_function

def optional_auth(f):
    """Decorator for optional authentication (user can be logged in or not)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            user_data = auth_service.get_current_user_from_token()
            request.current_user = user_data  # Will be None if not authenticated
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"Optional auth error: {str(e)}")
            request.current_user = None
            return f(*args, **kwargs)
    
    return decorated_function

def get_current_user_id() -> Optional[int]:
    """Helper function to get current user ID from request"""
    if hasattr(request, 'current_user') and request.current_user:
        return request.current_user.get('user_id')
    return None

def get_current_user_email() -> Optional[str]:
    """Helper function to get current user email from request"""
    if hasattr(request, 'current_user') and request.current_user:
        return request.current_user.get('email')
    return None
