"""
User Model for Task Manager API
Represents a user with authentication and profile information
"""

from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
import json
import hashlib
import secrets

@dataclass
class User:
    email: str
    name: str
    password_hash: Optional[str] = None
    created_at: datetime = None
    updated_at: Optional[datetime] = None
    id: Optional[int] = None
    is_active: bool = True
    timezone: str = 'UTC'
    notification_preferences: str = 'both'  # email, calendar, both, none
    google_credentials: Optional[str] = None
    google_calendar_enabled: bool = False
    google_sheets_enabled: bool = False
    google_gmail_enabled: bool = False
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create User from dictionary"""
        user_data = data.copy()
        
        # Handle date parsing
        if 'created_at' in user_data and user_data['created_at']:
            if isinstance(user_data['created_at'], str):
                dt = datetime.fromisoformat(user_data['created_at'].replace('Z', '+00:00'))
                user_data['created_at'] = dt.replace(tzinfo=None) if dt.tzinfo else dt
        
        if 'updated_at' in user_data and user_data['updated_at']:
            if isinstance(user_data['updated_at'], str):
                user_data['updated_at'] = datetime.fromisoformat(user_data['updated_at'].replace('Z', '+00:00'))
        
        return cls(**user_data)
    
    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> 'User':
        """Create User from database row"""
        user_data = dict(row)
        
        # Parse datetime strings from database
        if user_data.get('created_at'):
            user_data['created_at'] = datetime.fromisoformat(user_data['created_at'])
        
        if user_data.get('updated_at'):
            user_data['updated_at'] = datetime.fromisoformat(user_data['updated_at'])
        
        # Filter to only include fields that exist in the User dataclass
        valid_fields = {
            'email', 'name', 'password_hash', 'created_at', 'updated_at', 
            'id', 'is_active', 'timezone', 'notification_preferences',
            'google_credentials', 'google_calendar_enabled', 'google_sheets_enabled', 'google_gmail_enabled'
        }
        filtered_data = {k: v for k, v in user_data.items() if k in valid_fields}
        
        return cls(**filtered_data)
    
    def to_dict(self, include_password=False) -> Dict[str, Any]:
        """Convert User to dictionary"""
        result = asdict(self)
        
        # Remove password hash unless explicitly requested
        if not include_password and 'password_hash' in result:
            del result['password_hash']
        
        # Convert datetime objects to ISO strings
        if result.get('created_at'):
            result['created_at'] = result['created_at'].isoformat()
        
        if result.get('updated_at'):
            result['updated_at'] = result['updated_at'].isoformat()
        
        return result
    
    def to_json(self, include_password=False) -> str:
        """Convert User to JSON string"""
        return json.dumps(self.to_dict(include_password), indent=2)
    
    def set_password(self, password: str) -> None:
        """Set password hash for the user"""
        # Generate a random salt
        salt = secrets.token_hex(16)
        # Create password hash with salt
        password_with_salt = f"{password}{salt}"
        self.password_hash = f"{salt}:{hashlib.sha256(password_with_salt.encode()).hexdigest()}"
    
    def check_password(self, password: str) -> bool:
        """Check if provided password matches stored hash"""
        if not self.password_hash:
            return False
        
        try:
            salt, stored_hash = self.password_hash.split(':', 1)
            password_with_salt = f"{password}{salt}"
            computed_hash = hashlib.sha256(password_with_salt.encode()).hexdigest()
            return computed_hash == stored_hash
        except ValueError:
            return False
    
    def validate_email(self) -> bool:
        """Validate email format"""
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, self.email) is not None
    
    def update_last_activity(self) -> None:
        """Update the updated_at timestamp"""
        self.updated_at = datetime.now()
