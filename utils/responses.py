"""
API Response utilities for Task Manager API
Standardized response formatting for consistent API responses
"""

from flask import jsonify
from datetime import datetime
from typing import Any, Dict, List, Union

class APIResponse:
    
    @staticmethod
    def success(data: Any = None, status_code: int = 200) -> tuple:
        """Create a successful API response"""
        response = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'status_code': status_code
        }
        
        if data is not None:
            response['data'] = data
        
        return jsonify(response), status_code
    
    @staticmethod
    def error(message: Union[str, List[str]], status_code: int = 400, error_code: str = None) -> tuple:
        """Create an error API response"""
        response = {
            'success': False,
            'timestamp': datetime.now().isoformat(),
            'status_code': status_code
        }
        
        if isinstance(message, list):
            response['errors'] = message
        else:
            response['error'] = message
        
        if error_code:
            response['error_code'] = error_code
        
        return jsonify(response), status_code
    
    @staticmethod
    def paginated_success(data: List[Any], page: int, per_page: int, total: int, status_code: int = 200) -> tuple:
        """Create a paginated successful response"""
        response = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'status_code': status_code,
            'data': data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': (total + per_page - 1) // per_page,
                'has_next': page * per_page < total,
                'has_prev': page > 1
            }
        }
        
        return jsonify(response), status_code
    
    @staticmethod
    def validation_error(errors: List[str]) -> tuple:
        """Create a validation error response"""
        return APIResponse.error(errors, 400, "VALIDATION_ERROR")
    
    @staticmethod
    def not_found(resource: str = "Resource") -> tuple:
        """Create a not found error response"""
        return APIResponse.error(f"{resource} not found", 404, "NOT_FOUND")
    
    @staticmethod
    def unauthorized(message: str = "Unauthorized") -> tuple:
        """Create an unauthorized error response"""
        return APIResponse.error(message, 401, "UNAUTHORIZED")
    
    @staticmethod
    def forbidden(message: str = "Forbidden") -> tuple:
        """Create a forbidden error response"""
        return APIResponse.error(message, 403, "FORBIDDEN")
    
    @staticmethod
    def internal_error(message: str = "Internal server error") -> tuple:
        """Create an internal server error response"""
        return APIResponse.error(message, 500, "INTERNAL_ERROR")
    
    @staticmethod
    def bad_request(message: str = "Bad request") -> tuple:
        """Create a bad request error response"""
        return APIResponse.error(message, 400, "BAD_REQUEST")
    
    @staticmethod
    def conflict(message: str = "Conflict") -> tuple:
        """Create a conflict error response"""
        return APIResponse.error(message, 409, "CONFLICT")
    
    @staticmethod
    def service_unavailable(message: str = "Service temporarily unavailable") -> tuple:
        """Create a service unavailable error response"""
        return APIResponse.error(message, 503, "SERVICE_UNAVAILABLE")
    
    @staticmethod
    def rate_limited(message: str = "Rate limit exceeded") -> tuple:
        """Create a rate limited error response"""
        return APIResponse.error(message, 429, "RATE_LIMITED")
