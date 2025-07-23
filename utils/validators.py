"""
Validators for Task Manager API
Handles input validation for task operations
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List
import re

class TaskValidator:
    
    VALID_PRIORITIES = ['low', 'medium', 'high']
    VALID_STATUSES = ['pending', 'in_progress', 'completed']
    
    def validate_create_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate task creation data"""
        errors = []
        
        # Required fields
        if not data:
            errors.append("Request body is required")
            return {'valid': False, 'errors': errors}
        
        # Title validation
        title = data.get('title', '').strip()
        if not title:
            errors.append("Title is required")
        elif len(title) > 200:
            errors.append("Title must be less than 200 characters")
        
        # Description validation
        description = data.get('description')
        if description and len(description) > 1000:
            errors.append("Description must be less than 1000 characters")
        
        # Priority validation
        priority = data.get('priority', 'medium')
        if priority not in self.VALID_PRIORITIES:
            errors.append(f"Priority must be one of: {', '.join(self.VALID_PRIORITIES)}")
        
        # Status validation
        status = data.get('status', 'pending')
        if status not in self.VALID_STATUSES:
            errors.append(f"Status must be one of: {', '.join(self.VALID_STATUSES)}")
        
        # Due date validation
        due_date = data.get('due_date')
        if due_date:
            if not self._validate_date_format(due_date):
                errors.append("Due date must be in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)")
            else:
                try:
                    parsed_date = self._parse_date(due_date)
                    # Allow past dates for flexibility, but warn if too far in past
                    if parsed_date and parsed_date < datetime.now() - timedelta(days=365):
                        errors.append("Due date cannot be more than a year in the past")
                except ValueError:
                    errors.append("Invalid due date format")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def validate_update_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate task update data"""
        errors = []
        
        if not data:
            errors.append("Request body is required")
            return {'valid': False, 'errors': errors}
        
        # Title validation (if provided)
        if 'title' in data:
            title = data['title'].strip() if data['title'] else ''
            if not title:
                errors.append("Title cannot be empty")
            elif len(title) > 200:
                errors.append("Title must be less than 200 characters")
        
        # Description validation (if provided)
        if 'description' in data and data['description'] and len(data['description']) > 1000:
            errors.append("Description must be less than 1000 characters")
        
        # Priority validation (if provided)
        if 'priority' in data and data['priority'] not in self.VALID_PRIORITIES:
            errors.append(f"Priority must be one of: {', '.join(self.VALID_PRIORITIES)}")
        
        # Status validation (if provided)
        if 'status' in data and data['status'] not in self.VALID_STATUSES:
            errors.append(f"Status must be one of: {', '.join(self.VALID_STATUSES)}")
        
        # Due date validation (if provided)
        if 'due_date' in data and data['due_date']:
            if not self._validate_date_format(data['due_date']):
                errors.append("Due date must be in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)")
            else:
                try:
                    parsed_date = self._parse_date(data['due_date'])
                    if parsed_date and parsed_date < datetime.now() - timedelta(days=365):
                        errors.append("Due date cannot be more than a year in the past")
                except ValueError:
                    errors.append("Invalid due date format")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_batch_email_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate batch email data"""
        errors = []
        
        if not data:
            errors.append("Request body is required")
            return {'valid': False, 'errors': errors}
        
        recipient_email = data.get('recipient_email')
        if not recipient_email:
            errors.append("recipient_email is required")
        elif not self.validate_email(recipient_email):
            errors.append("Invalid email format")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def validate_export_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate export to sheets data"""
        errors = []
        
        # Spreadsheet name validation (if provided)
        if data and 'spreadsheet_name' in data:
            name = data['spreadsheet_name']
            if name and (len(name) > 100 or len(name.strip()) == 0):
                errors.append("Spreadsheet name must be between 1 and 100 characters")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def validate_calendar_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate calendar event data"""
        errors = []
        
        # Optional validations for calendar event customization
        if data:
            # Duration validation (if provided)
            if 'duration_minutes' in data:
                duration = data['duration_minutes']
                if not isinstance(duration, int) or duration < 15 or duration > 1440:
                    errors.append("Duration must be between 15 and 1440 minutes (1 day)")
            
            # Reminder validation (if provided)
            if 'reminder_minutes' in data:
                reminder = data['reminder_minutes']
                if not isinstance(reminder, int) or reminder < 0 or reminder > 40320:
                    errors.append("Reminder must be between 0 and 40320 minutes (4 weeks)")
            
            # Location validation (if provided)
            if 'location' in data and data['location'] and len(data['location']) > 255:
                errors.append("Location must be less than 255 characters")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _validate_date_format(self, date_str: str) -> bool:
        """Validate date string format"""
        if not isinstance(date_str, str):
            return False
        
        # Try various ISO formats
        formats = [
            '%Y-%m-%d',
            '%Y-%m-%dT%H:%M',          # HTML datetime-local format
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S.%fZ'
        ]
        
        for fmt in formats:
            try:
                datetime.strptime(date_str, fmt)
                return True
            except ValueError:
                continue
        
        return False
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object"""
        if not date_str:
            return None
        
        # Try ISO format first
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except ValueError:
            pass
        
        # Try various formats
        formats = [
            '%Y-%m-%d',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse date: {date_str}")
    
    def sanitize_input(self, text: str) -> str:
        """Sanitize text input"""
        if not text:
            return ""
        
        # Remove potentially dangerous characters
        text = text.strip()
        
        # Remove any null bytes
        text = text.replace('\x00', '')
        
        return text
